from http.server import BaseHTTPRequestHandler
import json
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, date
import calendar
import statistics
import math

# Load environment variables (works locally, Vercel uses os.environ directly)
# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
env_options = [
    os.path.join(script_dir, "..", "..", ".env"),
    os.path.join(script_dir, "..", ".env"),
    os.path.join(os.getcwd(), ".env")
]
for path in env_options:
    if os.path.exists(path):
        load_dotenv(path)
        print(f"INFO: Loaded .env from {path}")
        break
else:
    load_dotenv() # Fallback

# ===================================================================
# CONSTANTES GLOBALES
# ===================================================================
META_GLOBAL_110 = 1707  # Meta total mensual (110%)
CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month  # Dinámico - mes actual

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

# ===================================================================
# NORMALIZACIÓN Z-SCORE
# ===================================================================
def normalize_z_score(values, inverse=False):
    """
    Normaliza valores usando z-score con transformación sigmoide.
    Retorna valores entre ~0 y 1.
    
    Args:
        values: Lista de valores a normalizar
        inverse: Si True, invierte la escala (para métricas donde menor es mejor)
    """
    if not values or len(values) < 2:
        return [0.5] * len(values)
    
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 1.0
    
    if stdev == 0:
        return [0.5] * len(values)
    
    z_scores = [(v - mean) / stdev for v in values]
    normalized = [(math.tanh(z / 2) + 1) / 2 for z in z_scores]
    
    if inverse:
        normalized = [1 - n for n in normalized]
    
    return normalized

def fetch_squad_intelligence(coordinador_email="carlos.echeverria"):
    """
    Sistema de Inteligencia con Scoring Robusto Fase 1
    - Engagement (35 pts)
    - Rendimiento (40 pts)
    """
    debug_log = []
    conn = None
    cursor = None
    
    try:
        debug_log.append("Connecting to DB...")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        debug_log.append("Connected.")
        
        # ================================================================
        # PASO 1: Participación Histórica & Meta Equipo
        # ================================================================
        debug_log.append("Query 1: Participación histórica")
        cursor.execute('SELECT SUM(reserva) as total_global FROM bi_DimCorredores WHERE activo = 1')
        total_global_hist = float(cursor.fetchone()['total_global'] or 1)
        
        cursor.execute('SELECT SUM(reserva) as total_equipo FROM bi_DimCorredores WHERE coordinador = %s AND activo = 1', (coordinador_email,))
        total_equipo_hist = float(cursor.fetchone()['total_equipo'] or 0)
        
        pct_equipo = total_equipo_hist / total_global_hist if total_global_hist > 0 else 0
        META_EQUIPO = int(META_GLOBAL_110 * pct_equipo)
        
        # ================================================================
        # PASO 2: Contratos del Equipo (Mes Actual)
        # ================================================================
        debug_log.append("Query 2: Contratos equipo mes")
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
        contratos_equipo_mes = int(cursor.fetchone()['contratos_mes'] or 0)
        
        # ================================================================
        # PASO 3: Data Individual Base (Contratos, Leads, Prospectos)
        # ================================================================
        debug_log.append("Query 3: Data individual base")
        cursor.execute('''
            SELECT 
                c.corredor_id,
                c.nombre_corredor,
                c.reserva as reservas_historicas,
                COALESCE(l.contratos_mes, 0) as contratos_mes,
                COALESCE(l.leads_tomados_mes, 0) as leads_tomados_mes,
                COALESCE(l.prospectos_mes, 0) as prospectos_mes,
                COALESCE(l.leads_descartados_sin_gestion, 0) as leads_descartados,
                COALESCE(l.prospectos_descartados, 0) as prospectos_descartados,
                COALESCE(l.contacto_24h, 0) as contacto_24h
            FROM bi_DimCorredores c
            LEFT JOIN (
                SELECT 
                    corredor_id,
                    COUNT(DISTINCT CASE WHEN contrato_created_at IS NOT NULL THEN lead_id END) as contratos_mes,
                    COUNT(DISTINCT lead_id) as leads_tomados_mes,
                    COUNT(DISTINCT CASE WHEN step_3_prospecto = 1 THEN lead_id END) as prospectos_mes,
                    SUM(CASE WHEN step_1_epc_descartado = 1 AND lag_contacto IS NULL THEN 1 ELSE 0 END) as leads_descartados_sin_gestion,
                    SUM(CASE WHEN step_3_prospecto_descartado = 1 THEN 1 ELSE 0 END) as prospectos_descartados,
                    SUM(CASE WHEN lag_contacto IS NOT NULL AND lag_contacto <= 24 THEN 1 ELSE 0 END) as contacto_24h
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
        
        # ================================================================
        # PASO 4: Visitas (Agendas)
        # ================================================================
        debug_log.append("Query 4: Visitas mes")
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
        
        debug_log.append("Calculating raw metrics...")
        
        # ================================================================
        # PASO 5: Calcular métricas RAW para cada corredor
        # ================================================================
        dias_restantes = calculate_dias_restantes()
        brokers_raw = []
        
        for corredor in corredores_data:
            corredor_id = str(corredor['corredor_id'])
            
            # Meta personalizada
            reservas_hist = float(corredor['reservas_historicas'] or 0)
            pct_corredor = reservas_hist / total_equipo_hist if total_equipo_hist > 0 else 0
            meta_corredor = int(META_EQUIPO * pct_corredor)
            
            # Conversiones básicas de Decimal a int/float
            contratos_mes = int(corredor['contratos_mes'] or 0)
            leads_mes = int(corredor['leads_tomados_mes'] or 0)
            prospectos_mes = int(corredor['prospectos_mes'] or 0)
            leads_descartados = int(corredor['leads_descartados'] or 0)
            prospectos_descartados = int(corredor['prospectos_descartados'] or 0)
            contacto_24h = int(corredor['contacto_24h'] or 0)
            
            # Visitas
            visit_data = visit_metrics.get(corredor_id, {})
            total_agendas = int(visit_data.get('total_agendas', 0) or 1)  # Evitar div/0
            visitas_realizadas = int(visit_data.get('visitas_realizadas', 0) or 0)
            visitas_canceladas = int(visit_data.get('visitas_canceladas', 0) or 0)
            
            # === ENGAGEMENT METRICS (RAW) ===
            tasa_visitas = visitas_realizadas / total_agendas if total_agendas > 0 else 0
            tasa_no_cancela = 1 - (visitas_canceladas / total_agendas) if total_agendas > 0 else 1
            tasa_no_descarta_leads = 1 - (leads_descartados / leads_mes) if leads_mes > 0 else 1
            tasa_no_descarta_prospectos = 1 - (prospectos_descartados / prospectos_mes) if prospectos_mes > 0 else 1
            tasa_contacto_24h = contacto_24h / leads_mes if leads_mes > 0 else 0
            
            # === RENDIMIENTO METRICS (RAW) ===
            conv_prospecto_contrato = contratos_mes / prospectos_mes if prospectos_mes > 0 else 0
            conv_lead_contrato = contratos_mes / leads_mes if leads_mes > 0 else 0
            contratos_absolutos = contratos_mes  # Valor absoluto (no tasa)
            leads_por_visita = leads_mes / visitas_realizadas if visitas_realizadas > 0 else 0
            
            # ===  Datos Operativos ===
            faltante = max(meta_corredor - contratos_mes, 0)
            conv_mes = (prospectos_mes / leads_mes * 100) if leads_mes > 0 else 0
            leads_diarios_necesarios = int((faltante / dias_restantes) / (conv_mes / 100)) if conv_mes > 0 else 0
            
            brokers_raw.append({
                'corredor_id': corredor_id,
                'nombre': corredor['nombre_corredor'],
                'meta_personal': meta_corredor,
                'contratos_mes': contratos_mes,
                'faltante': faltante,
                'leads_mes': leads_mes,
                'prospectos_mes': prospectos_mes,
                'conversion': f"{conv_mes:.1f}",
                'visitas_realizadas': visitas_realizadas,
                'visitas_canceladas': visitas_canceladas,
                'leads_diarios_necesarios': leads_diarios_necesarios,
                # Métricas RAW Engagement
                'tasa_visitas': tasa_visitas,
                'tasa_no_cancela': tasa_no_cancela,
                'tasa_no_descarta_leads': tasa_no_descarta_leads,
                'tasa_no_descarta_prospectos': tasa_no_descarta_prospectos,
                'tasa_contacto_24h': tasa_contacto_24h,
                # Métricas RAW Rendimiento
                'conv_prospecto_contrato': conv_prospecto_contrato,
                'conv_lead_contrato': conv_lead_contrato,
                'contratos_absolutos': contratos_absolutos,
                'leads_por_visita': leads_por_visita
            })
        
        # ================================================================
        # PASO 6: NORMALIZACIÓN Z-SCORE DE MÉTRICAS
        # ================================================================
        debug_log.append("Normalizing metrics...")
        
        # Extraer todas las métricas en listas
        all_tasa_visitas = [b['tasa_visitas'] for b in brokers_raw]
        all_tasa_no_cancela = [b['tasa_no_cancela'] for b in brokers_raw]
        all_tasa_no_descarta_leads = [b['tasa_no_descarta_leads'] for b in brokers_raw]
        all_tasa_no_descarta_prospectos = [b['tasa_no_descarta_prospectos'] for b in brokers_raw]
        all_tasa_contacto_24h = [b['tasa_contacto_24h'] for b in brokers_raw]
        
        all_conv_p_c = [b['conv_prospecto_contrato'] for b in brokers_raw]
        all_conv_l_c = [b['conv_lead_contrato'] for b in brokers_raw]
        all_contratos_abs = [b['contratos_absolutos'] for b in brokers_raw]
        all_lpv = [b['leads_por_visita'] for b in brokers_raw]
        
        # Normalizar
        norm_tasa_visitas = normalize_z_score(all_tasa_visitas)
        norm_tasa_no_cancela = normalize_z_score(all_tasa_no_cancela)
        norm_tasa_no_descarta_leads = normalize_z_score(all_tasa_no_descarta_leads)
        norm_tasa_no_descarta_prospectos = normalize_z_score(all_tasa_no_descarta_prospectos)
        norm_tasa_contacto_24h = normalize_z_score(all_tasa_contacto_24h)
        
        norm_conv_p_c = normalize_z_score(all_conv_p_c)
        norm_conv_l_c = normalize_z_score(all_conv_l_c)
        norm_contratos_abs = normalize_z_score(all_contratos_abs)
        norm_lpv = normalize_z_score(all_lpv)
        
        # ================================================================
        # PASO 7: CALCULAR SCORES FINALES
        # ================================================================
        debug_log.append("Calculating scores...")
        brokers_final = []
        
        for i, broker_raw in enumerate(brokers_raw):
            # ENGAGEMENT (35 pts total)
            eng_visitas = norm_tasa_visitas[i] * 10
            eng_no_cancela = norm_tasa_no_cancela[i] * 8
            eng_no_descarta_leads = norm_tasa_no_descarta_leads[i] * 7
            eng_no_descarta_prospectos = norm_tasa_no_descarta_prospectos[i] * 5
            eng_contacto_24h = norm_tasa_contacto_24h[i] * 5
            
            engagement_score = eng_visitas + eng_no_cancela + eng_no_descarta_leads + eng_no_descarta_prospectos + eng_contacto_24h
            
            # RENDIMIENTO (40 pts total)
            rend_conv_p_c = norm_conv_p_c[i] * 15
            rend_conv_l_c = norm_conv_l_c[i] * 10
            rend_contratos_abs = norm_contratos_abs[i] * 10
            rend_lpv = norm_lpv[i] * 5
            
            rendimiento_score = rend_conv_p_c + rend_conv_l_c + rend_contratos_abs + rend_lpv
            
            # TOTAL (75 pts - Fase 1)
            total_score = engagement_score + rendimiento_score
            
            # Acción Sugerida
            if broker_raw['contratos_mes'] >= broker_raw['meta_personal']:
                action = "¡Meta Cumplida!"
            elif broker_raw['leads_diarios_necesarios'] > 0:
                action = f"Asignar {broker_raw['leads_diarios_necesarios']} leads/día"
            else:
                action = "Revisar Conversión"
            
            brokers_final.append({
                "name": broker_raw['nombre'],
                "leads": broker_raw['leads_mes'],
                "reservas": broker_raw['contratos_mes'],
                "meta_personal": broker_raw['meta_personal'],
                "faltante": broker_raw['faltante'],
                "conversion": broker_raw['conversion'],
                "leadsNeeded": broker_raw['leads_diarios_necesarios'],
                "action": action,
                "score": round(total_score, 2),
                "score_engagement": round(engagement_score, 2),
                "score_rendimiento": round(rendimiento_score, 2),
                "visitas_realizadas": broker_raw['visitas_realizadas'],
                "breakdown_engagement": {
                    "visitas_realizadas": round(eng_visitas, 2),
                    "visitas_no_canceladas": round(eng_no_cancela, 2),
                    "no_descarta_leads": round(eng_no_descarta_leads, 2),
                    "no_descarta_prospectos": round(eng_no_descarta_prospectos, 2),
                    "contacto_24h": round(eng_contacto_24h, 2)
                },
                "breakdown_rendimiento": {
                    "conv_prospecto_contrato": round(rend_conv_p_c, 2),
                    "conv_lead_contrato": round(rend_conv_l_c, 2),
                    "contratos_absolutos": round(rend_contratos_abs, 2),
                    "leads_por_visita": round(rend_lpv, 2)
                }
            })
        
        cursor.close()
        conn.close()
        
        return {
            "brokers": brokers_final,
            "squad_summary": {
                "meta_equipo": META_EQUIPO,
                "contratos_actuales": contratos_equipo_mes,
                "faltante_equipo": max(META_EQUIPO - contratos_equipo_mes, 0),
                "dias_restantes": dias_restantes,
                "debug_log": debug_log,
                "scoring_version": "Phase 1 - Engagement (35) + Rendimiento (40) = 75 pts"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return {"error": str(e), "debug_log": debug_log}

# ===================================================================
# VERCEL SERVERLESS HANDLER
# ===================================================================
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Endpoint: GET /api/v2_intelligence
        """
        try:
            data = fetch_squad_intelligence("carlos.echeverria")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            self.wfile.write(json.dumps(data, default=str).encode())
            
        except Exception as e:
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
