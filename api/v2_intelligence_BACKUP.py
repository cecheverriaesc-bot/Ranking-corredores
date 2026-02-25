from http.server import BaseHTTPRequestHandler
import json
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def get_bi_connection():
    """
    Conecta a la base de datos bi_assetplan (BI procesada).
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=int(os.getenv("DB_PORT", 3306)),
        database="bi_assetplan"
    )

def calculate_leads_needed(current_reservas, target_reservas, conversion_rate_str):
    """
    Calcula cuántos leads adicionales necesita un corredor para cumplir meta.
    
    Args:
        current_reservas: Reservas actuales del corredor
        target_reservas: Meta de reservas (ej: 7)
        conversion_rate_str: Porcentaje de conversión como string (ej: "8.5")
    
    Returns:
        Leads necesarios (int)
    """
    try:
        conversion_rate = float(conversion_rate_str) / 100 if conversion_rate_str else 0.0
    except:
        conversion_rate = 0.0
    
    if conversion_rate <= 0:
        return 999  # Conversión inválida o cero
    
    gap = max(0, target_reservas - current_reservas)
    return int(gap / conversion_rate)

def fetch_squad_intelligence(coordinador_email="carlos.echeverria"):
    """
    Obtiene métricas de inteligencia para Squad Carlos.
    
    Returns:
        {
            "brokers": [...],      # Lista de corredores con métricas calculadas
            "coverage": [...],     # Stock por comuna vs corredores activos
            "efficiency_alerts": {...}  # Alertas de eficiencia
        }
    """
    conn = get_bi_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # ====================================================================
        # QUERY 1: Base Metrics from bi_DimCorredores
        # ====================================================================
        cursor.execute("""
            SELECT 
                corredor_id,
                nombre_corredor,
                cant_leads,
                reserva,
                porcentaje_convertido_prospecto,
                porcentaje_convertido_contrato,
                prospectos_sin_gestion,
                agendas_corredor,
                porcentaje_prospectos_sin_gestion,
                porcentaje_cerrados_inactividad,
                porcentaje_cerrados_no_contactado
            FROM bi_DimCorredores
            WHERE coordinador = %s 
              AND activo = 1
            ORDER BY reserva DESC
        """, (coordinador_email,))
        
        brokers_raw = cursor.fetchall()
        
        # ====================================================================
        # QUERY 2: Visit Metrics from bi_DimAgendas
        # ====================================================================
        cursor.execute("""
            SELECT 
                corredor_id,
                COUNT(*) as total_agendas,
                SUM(CASE WHEN estado = 'Visitado' THEN 1 ELSE 0 END) as visitas_realizadas,
                SUM(CASE WHEN estado = 'Cancelado' THEN 1 ELSE 0 END) as visitas_canceladas
            FROM bi_DimAgendas
            WHERE corredor_id IS NOT NULL
            GROUP BY corredor_id
        """)
        
        visit_metrics = {str(row['corredor_id']): row for row in cursor.fetchall()}
        
        # ====================================================================
        # QUERY 3: Lead Response Time from bi_DimLeads
        # ====================================================================
        cursor.execute("""
            SELECT 
                corredor_id,
                COUNT(*) as total_leads_contacto,
                SUM(CASE WHEN lag_contacto IS NOT NULL AND lag_contacto <= 24 THEN 1 ELSE 0 END) as contacto_24h,
                SUM(step_1_epc_tomado) as leads_tomados
            FROM bi_DimLeads
            WHERE corredor_id IS NOT NULL
            GROUP BY corredor_id
        """)
        
        lead_metrics = {str(row['corredor_id']): row for row in cursor.fetchall()}
        
        # Calculate max reservas for normalization
        max_reservas = max([b['reserva'] or 0 for b in brokers_raw]) if brokers_raw else 1
        
        # ====================================================================
        # SCORING CALCULATION WITH ALL METRICS
        # ====================================================================
        TARGET_RESERVAS = 7
        brokers = []
        for broker in brokers_raw:
            # Get corredor_id for proper matching
            corredor_id = str(broker['corredor_id']) if broker['corredor_id'] else None
            broker_name = broker['nombre_corredor']
            
            # Match with visit and lead metrics using corredor_id
            visits = visit_metrics.get(corredor_id) if corredor_id else None
            leads = lead_metrics.get(corredor_id) if corredor_id else None
            
            # Conversión rates (from bi_DimCorredores)
            conv_prospecto = float(broker['porcentaje_convertido_prospecto'] or 0)
            conv_contrato = float(broker['porcentaje_convertido_contrato'] or 0)
            sin_gestion_pct = float(broker['porcentaje_prospectos_sin_gestion'] or 0) / 100
            cerrados_inactividad = float(broker['porcentaje_cerrados_inactividad'] or 0) / 100
            cerrados_no_contactado = float(broker['porcentaje_cerrados_no_contactado'] or 0) / 100
            
            # PILAR 1: Engagement & Gestión (35%) - COMPLETE NOW
            engagement_components = {}
            
            # 1.1 Visit completion rate (30% of engagement)
            if visits and visits['total_agendas'] > 0:
                visit_completion = float(visits['visitas_realizadas']) / float(visits['total_agendas'])
                visit_cancellation = float(visits['visitas_canceladas']) / float(visits['total_agendas'])
                engagement_components['visitas_realizadas'] = visit_completion * 0.30
                engagement_components['visitas_no_canceladas'] = max(0, 1 - visit_cancellation) * 0.25
            else:
                engagement_components['visitas_realizadas'] = 0
                engagement_components['visitas_no_canceladas'] = 0
            
            # 1.2 Lead response <24h (25% of engagement)
            if leads and leads['total_leads_contacto'] > 0:
                response_24h_rate = float(leads['contacto_24h']) / float(leads['total_leads_contacto'])
                engagement_components['respuesta_24h'] = response_24h_rate * 0.25
            else:
                engagement_components['respuesta_24h'] = 0
            
            # 1.3 Active management (20% of engagement)
            descartados_pct = cerrados_inactividad + cerrados_no_contactado
            engagement_components['gestion_activa'] = max(0, 1 - sin_gestion_pct) * 0.10
            engagement_components['no_descarta'] = max(0, 1 - descartados_pct) * 0.10
            
            engagement_score = sum(engagement_components.values()) * 0.35
            
            # PILAR 2: Rendimiento & Conversión (40%) - COMPLETE NOW
            reservas_norm = (broker['reserva'] or 0) / max(max_reservas, 1)
            
            # 2.1 Conversion efficiency (50%)
            rendimiento_components = {
                'conv_prospecto_reserva': (conv_prospecto / 100) * 0.35,
                'conv_lead_contrato': (conv_contrato / 100) * 0.15
            }
            
            # 2.2 Absolute productivity (30%)
            rendimiento_components['reservas_absolutas'] = reservas_norm * 0.30
            
            # 2.3 Leads taken per visit efficiency (20%)
            if visits and leads and visits['visitas_realizadas'] > 0:
                leads_per_visit = float(leads['leads_tomados'] or 0) / float(visits['visitas_realizadas'])
                # Normalize assuming 5 leads per visit is excellent
                leads_per_visit_norm = min(1.0, leads_per_visit / 5.0)
                rendimiento_components['productividad_visitas'] = leads_per_visit_norm * 0.20
            else:
                rendimiento_components['productividad_visitas'] = 0
            
            rendimiento_score = sum(rendimiento_components.values()) * 0.40
            
            # SCORE FINAL (75% - Pilar Operativo pending)
            broker_score = engagement_score + rendimiento_score
            
            # Categorization
            if broker_score >= 0.25:
                categoria = "Top Performer"
            elif broker_score >= 0.15:
                categoria = "Promedio"
            else:
                categoria = "Coaching"
            
            # Leads needed calculation
            leads_needed = calculate_leads_needed(
                broker['reserva'] or 0,
                TARGET_RESERVAS,
                broker['porcentaje_convertido_prospecto']
            )
            
            # Action suggestion with score
            if broker['reserva'] >= TARGET_RESERVAS:
                action = "Meta Cumplida"
            elif broker_score < 0.10:
                action = "Coaching Urgente"
            elif leads_needed > 50:
                action = "Revisar Conversión"
            else:
                action = f"Asignar +{leads_needed} Leads"
            
            brokers.append({
                "name": broker_name,
                "leads": broker['cant_leads'] or 0,
                "reservas": broker['reserva'] or 0,
                "conversion": broker['porcentaje_convertido_prospecto'] or "0",
                "leadsNeeded": leads_needed,
                "action": action,
                "prospectos_sin_gestion": broker['prospectos_sin_gestion'] or 0,
                "score": round(broker_score, 3),
                "score_engagement": round(engagement_score, 3),
                "score_rendimiento": round(rendimiento_score, 3),
                "categoria": categoria,
                # Detailed breakdown for frontend tooltip
                "breakdown_engagement": {
                    "visitas_realizadas": round(engagement_components.get('visitas_realizadas', 0), 3),
                    "visitas_no_canceladas": round(engagement_components.get('visitas_no_canceladas', 0), 3),
                    "respuesta_24h": round(engagement_components.get('respuesta_24h', 0), 3),
                    "gestion_activa": round(engagement_components.get('gestion_activa', 0), 3),
                    "no_descarta": round(engagement_components.get('no_descarta', 0), 3)
                },
                "breakdown_rendimiento": {
                    "conv_prospecto_reserva": round(rendimiento_components.get('conv_prospecto_reserva', 0), 3),
                    "reservas_absolutas": round(rendimiento_components.get('reservas_absolutas', 0), 3),
                    "productividad_visitas": round(rendimiento_components.get('productividad_visitas', 0), 3),
                    "conv_lead_contrato": round(rendimiento_components.get('conv_lead_contrato', 0), 3)
                }
            })
        
        # ====================================================================
        # QUERY 2: Cobertura por Comuna (Stock vs Actividad)
        # ====================================================================
        current_year = datetime.now().year
        cursor.execute("""
            SELECT 
                l.comuna,
                COUNT(DISTINCT l.property_id) as stock_disponible,
                COUNT(DISTINCT a.corredor_id) as corredores_activos
            FROM bi_DimLeadAttemps l
            LEFT JOIN bi_DimAgendas a 
                ON l.property_id = a.property_id 
                AND YEAR(a.created_at) = %s
            WHERE YEAR(l.created_at) = %s
            GROUP BY l.comuna
            HAVING stock_disponible > 15  -- Solo comunas relevantes
            ORDER BY stock_disponible DESC
            LIMIT 20
        """, (current_year, current_year))
        
        coverage_raw = cursor.fetchall()
        coverage = []
        for item in coverage_raw:
            alert_level = "ok"
            if item['corredores_activos'] == 0:
                alert_level = "critical"
            elif item['stock_disponible'] / max(item['corredores_activos'], 1) > 30:
                alert_level = "warning"
            
            coverage.append({
                "comuna": item['comuna'],
                "stock": item['stock_disponible'],
                "activeBrokers": item['corredores_activos'],
                "alert": alert_level
            })
        
        # ====================================================================
        # QUERY 3: Alertas de Eficiencia
        # ====================================================================
        # Leads sin gestión > 24h (usando tabla de corredores agregada)
        cursor.execute("""
            SELECT SUM(prospectos_sin_gestion) as total_sin_gestion
            FROM bi_DimCorredores
            WHERE coordinador = %s AND activo = 1
        """, (coordinador_email,))
        
        leads_sin_gestion_result = cursor.fetchone()
        leads_sin_gestion = leads_sin_gestion_result['total_sin_gestion'] or 0
        
        # Unidades sin visitas en los últimos 15 días - QUERY REAL
        cursor.execute("""
            SELECT COUNT(DISTINCT la.property_id) as total_sin_visitas
            FROM bi_DimLeadAttemps la
            LEFT JOIN bi_DimAgendas ag 
                ON la.property_id = ag.property_id 
                AND ag.created_at >= DATE_SUB(CURDATE(), INTERVAL 15 DAY)
            WHERE YEAR(la.created_at) = YEAR(CURDATE())
              AND ag.id IS NULL
        """)
        
        unidades_result = cursor.fetchone()
        unidades_sin_visitas = unidades_result['total_sin_visitas'] or 0
        
        efficiency_alerts = {
            "leadsSinGestion": int(leads_sin_gestion),
            "unidadesSinVisitas": int(unidades_sin_visitas)
        }
        
        return {
            "brokers": brokers,
            "coverage": coverage,
            "efficiency_alerts": efficiency_alerts,
            "generated_at": datetime.now().isoformat()
        }
        
    finally:
        cursor.close()
        conn.close()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Endpoint: GET /api/v2_intelligence
        
        Retorna datos de inteligencia para el Laboratorio Estratégico.
        """
        try:
            # Fetch data from bi_assetplan
            data = fetch_squad_intelligence("carlos.echeverria")
            
            # Success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            self.wfile.write(json.dumps(data, default=str).encode())
            
        except Exception as e:
            # Error response
            print(f"ERROR in v2_intelligence: {str(e)}")
            import traceback
            traceback.print_exc()
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "error": str(e),
                "message": "Error fetching intelligence data"
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
