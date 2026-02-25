from http.server import BaseHTTPRequestHandler
import json
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, date
import calendar

# Load environment variables (works locally, Vercel uses os.environ directly)
load_dotenv()

# ===================================================================
# CONSTANTES GLOBALES
# ===================================================================
META_GLOBAL_110 = 1707  # Meta total mensual (110%)
CURRENT_YEAR = 2026
CURRENT_MONTH = 1  # Enero

def get_db_connection():
    """Get database connection with environment variables"""
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST') or os.getenv('DB_HOST'),
        user=os.environ.get('DB_USER') or os.getenv('DB_USER'),
        password=os.environ.get('DB_PASSWORD') or os.getenv('DB_PASSWORD'),
        port=int(os.environ.get('DB_PORT', 3306) or os.getenv('DB_PORT', 3306)),
        database='bi_assetplan'
    )

def calculate_dias_restantes():
    """Calcular días hábiles restantes del mes"""
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    dias_restantes = last_day - today.day
    return max(dias_restantes, 1)

def fetch_squad_intelligence(coordinador_email="carlos.echeverria"):
    debug_log = []
    conn = None
    cursor = None
    
    try:
        debug_log.append("Connecting to DB...")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        debug_log.append("Connected.")
        
        # 1. Participación Histórica
        debug_log.append("Query 1: Total Global")
        cursor.execute('SELECT SUM(reserva) as total_global FROM bi_DimCorredores WHERE activo = 1')
        total_global_hist = cursor.fetchone()['total_global'] or 1
        
        debug_log.append("Query 2: Total Equipo")
        cursor.execute('SELECT SUM(reserva) as total_equipo FROM bi_DimCorredores WHERE coordinador = %s AND activo = 1', (coordinador_email,))
        total_equipo_hist = cursor.fetchone()['total_equipo'] or 0
        
        pct_equipo = total_equipo_hist / total_global_hist if total_global_hist > 0 else 0
        META_EQUIPO = int(META_GLOBAL_110 * pct_equipo)
        
        # 2. Contratos Mes (Enero 2026)
        debug_log.append("Query 3: Contratos Mes")
        cursor.execute('''
            SELECT COUNT(DISTINCT lead_id) as contratos_mes
            FROM bi_DimLeads
            WHERE YEAR(contrato_created_at) = %s 
              AND MONTH(contrato_created_at) = %s
              AND corredor_id IN (
                  SELECT corredor_id FROM bi_DimCorredores 
                  WHERE coordinador = %s AND activo = 1
              )
        ''', (CURRENT_YEAR, CURRENT_MONTH, coordinador_email))
        contratos_equipo_mes = cursor.fetchone()['contratos_mes'] or 0
        
        # 3. Data Individual
        debug_log.append("Query 4: Data Individual")
        cursor.execute('''
            SELECT 
                c.corredor_id,
                c.nombre_corredor,
                c.reserva as reservas_historicas,
                COALESCE(l.contratos_mes, 0) as contratos_mes,
                COALESCE(l.leads_tomados_mes, 0) as leads_tomados_mes,
                COALESCE(l.prospectos_mes, 0) as prospectos_mes
            FROM bi_DimCorredores c
            LEFT JOIN (
                SELECT 
                    corredor_id,
                    COUNT(DISTINCT CASE WHEN contrato_created_at IS NOT NULL THEN lead_id END) as contratos_mes,
                    COUNT(DISTINCT lead_id) as leads_tomados_mes,
                    COUNT(DISTINCT CASE WHEN step_3_prospecto = 1 THEN lead_id END) as prospectos_mes
                FROM bi_DimLeads
                WHERE YEAR(fecha_tomado) = %s 
                  AND MONTH(fecha_tomado) = %s
                GROUP BY corredor_id
            ) l ON c.corredor_id = l.corredor_id
            WHERE c.coordinador = %s 
              AND c.activo = 1
            ORDER BY contratos_mes DESC, c.reserva DESC
        ''', (CURRENT_YEAR, CURRENT_MONTH, coordinador_email))
        corredores_data = cursor.fetchall()

        # 4. Visitas Mes
        debug_log.append("Query 5: Visitas Mes")
        cursor.execute('''
            SELECT 
                corredor_id,
                COUNT(*) as total_agendas,
                SUM(CASE WHEN estado = 'Visitado' THEN 1 ELSE 0 END) as visitas_realizadas,
                SUM(CASE WHEN estado = 'Cancelado' THEN 1 ELSE 0 END) as visitas_canceladas
            FROM bi_DimAgendas
            WHERE YEAR(agenda_fecha) = %s 
              AND MONTH(agenda_fecha) = %s
              AND corredor_id IS NOT NULL
            GROUP BY corredor_id
        ''', (CURRENT_YEAR, CURRENT_MONTH))
        visit_metrics = {str(row['corredor_id']): row for row in cursor.fetchall()}

        # 5. Leads Mes (Response Time check simplified)
        debug_log.append("Query 6: Leads Mes Response")
        cursor.execute('''
            SELECT 
                corredor_id,
                COUNT(*) as total_leads,
                SUM(CASE WHEN lag_contacto IS NOT NULL AND lag_contacto <= 24 THEN 1 ELSE 0 END) as contacto_24h
            FROM bi_DimLeads
            WHERE YEAR(fecha_tomado) = %s 
              AND MONTH(fecha_tomado) = %s
              AND corredor_id IS NOT NULL
            GROUP BY corredor_id
        ''', (CURRENT_YEAR, CURRENT_MONTH))
        lead_metrics = {str(row['corredor_id']): row for row in cursor.fetchall()}

        debug_log.append("Calculations...")
        dias_restantes = calculate_dias_restantes()
        brokers = []
        
        for corredor in corredores_data:
            corredor_id = str(corredor['corredor_id'])
            
            # Meta logic - Convert Decimals to float
            reservas_hist = float(corredor['reservas_historicas'] or 0)
            pct_corredor = reservas_hist / float(total_equipo_hist) if total_equipo_hist > 0 else 0
            meta_corredor = int(META_EQUIPO * pct_corredor)
            
            contratos_mes = int(corredor['contratos_mes'] or 0)
            faltante = max(meta_corredor - contratos_mes, 0)
            
            leads_mes = int(corredor['leads_tomados_mes'] or 0)
            prospectos_mes = int(corredor['prospectos_mes'] or 0)
            conv_mes = (prospectos_mes / leads_mes * 100) if leads_mes > 0 else 0
            
            leads_diarios_necesarios = int((faltante / dias_restantes) / (conv_mes / 100)) if conv_mes > 0 else 0
            
            # Metrics lookup - Convert all Decimals to int
            visit_data = visit_metrics.get(corredor_id, {})
            visitas_realizadas = int(visit_data.get('visitas_realizadas', 0) or 0)
            visitas_canceladas = int(visit_data.get('visitas_canceladas', 0) or 0)
            
            lead_data = lead_metrics.get(corredor_id, {})
            contacto_24h = int(lead_data.get('contacto_24h', 0) or 0)
            total_leads_contacto = int(lead_data.get('total_leads', 1) or 1)
            
            # Scoring Logic - All values are now int/float safe
            score_visit_vol = min(visitas_realizadas / 15, 1.0) * 0.30
            score_visit_cancel = (1 - (visitas_canceladas/visitas_realizadas)) * 0.25 if visitas_realizadas > 0 else 0
            score_response = (contacto_24h / total_leads_contacto) * 0.25
            
            engagement_score = score_visit_vol + score_visit_cancel + score_response + 0.10 + 0.10
            
            score_conv = min(conv_mes / 15, 1.0) * 0.35
            score_abs = min(contratos_mes / max(meta_corredor, 1), 1.0) * 0.30
            prod_val = (contratos_mes / visitas_realizadas) if visitas_realizadas > 0 else 0
            score_prod = min(prod_val / 0.10, 1.0) * 0.20
            
            rendimiento_score = score_conv + score_abs + score_prod + (score_conv * 0.4) 
            
            total_score = (engagement_score * 0.35) + (rendimiento_score * 0.40)
            
            # Action Text
            if contratos_mes >= meta_corredor:
                action = "Meta Cumplida!"
            elif leads_diarios_necesarios > 0:
                action = f"Asignar {leads_diarios_necesarios} leads/día"
            else:
                action = "Revisar Conversión"

            brokers.append({
                "name": corredor['nombre_corredor'],
                "leads": leads_mes,
                "reservas": contratos_mes,
                "meta_personal": meta_corredor,
                "faltante": faltante,
                "conversion": f"{conv_mes:.1f}",
                "leadsNeeded": leads_diarios_necesarios,
                "action": action,
                "score": round(total_score, 3),
                "score_engagement": round(engagement_score, 3),
                "score_rendimiento": round(rendimiento_score, 3),
                "visitas_realizadas": visitas_realizadas,
                "breakdown_engagement": {
                    "visitas_realizadas": round(score_visit_vol, 3), 
                    "visitas_no_canceladas": round(score_visit_cancel, 3),
                    "respuesta_24h": round(score_response, 3),
                    "gestion_activa": 0.1, "no_descarta": 0.1
                },
                "breakdown_rendimiento": {
                    "conv_prospecto_reserva": round(score_conv, 3),
                    "reservas_absolutas": round(score_abs, 3),
                    "productividad_visitas": round(score_prod, 3),
                    "conv_lead_contrato": round(score_conv * 0.4, 3) 
                }
            })
            
        debug_log.append("Finished Loop.")
        cursor.close()
        conn.close()
        
        return {
            "brokers": brokers, 
            "squad_summary": {
                "contratos_actuales": contratos_equipo_mes,
                "meta_equipo": META_EQUIPO,
                "faltante_equipo": max(META_EQUIPO - contratos_equipo_mes, 0),
                "debug_log": debug_log
            }
        }
        
    except Exception as e:
        if cursor: cursor.close()
        if conn: conn.close()
        return {"error": str(e), "debug_log": debug_log}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = fetch_squad_intelligence()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, default=str).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
