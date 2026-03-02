from http.server import BaseHTTPRequestHandler
import json
import mysql.connector
import os
from datetime import datetime, date
import calendar
import statistics
import math

# Import servicios centralizados
import sys
sys.path.append(os.path.dirname(__file__))
from services.metrics_service import (
    calculate_rate_with_smoothing,
    normalize_z_score_simple,
    get_contract_goal,
)
from utils.dates import (
    is_current_month,
    get_days_remaining_in_month,
)

# Load environment variables
def load_env_vars():
    env_vars = {}
    
    # Try to load from .env file for local development
    env_file_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                    
    # Push to os.environ so existing os.environ.get() calls work
    for k, v in env_vars.items():
        if k not in os.environ:
            os.environ[k] = v

load_env_vars()

# ===================================================================
# CONSTANTES GLOBALES
# ===================================================================
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

def calculate_dias_restantes(year=None, month=None):
    """
    Calcular días hábiles restantes del mes usando el servicio centralizado.
    """
    use_year = int(year) if year else CURRENT_YEAR
    use_month = int(month) if month else CURRENT_MONTH
    
    if not is_current_month(use_year, use_month):
        from datetime import date
        today = date.today()
        if use_year < today.year or (use_year == today.year and use_month < today.month):
            return 0
        return calendar.monthrange(use_year, use_month)[1]
        
    return get_days_remaining_in_month(use_year, use_month)

def fetch_squad_intelligence(coordinador_email="carlos.echeverria", year=None, month=None):
    """
    Sistema de Inteligencia con Scoring Robusto Fase 3 (Unificado)
    - Engagement (35 pts)
    - Rendimiento (40 pts)
    - Eficiencia (25 pts)
    """
    use_year = int(year) if year else CURRENT_YEAR
    use_month = int(month) if month else CURRENT_MONTH

    debug_log = []
    conn = None
    cursor = None
    
    try:
        debug_log.append(f"Connecting to DB... filtering by {use_year}-{month}")
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
        
        # Meta Global - Para 'all' sumamos las metas de los meses transcurridos (Ene-Mar 2026)
        if month == 'all':
            meta_global = sum([get_contract_goal(use_year, m) for m in range(1, CURRENT_MONTH + 1)])
        else:
            meta_global = get_contract_goal(use_year, use_month)
            
        META_EQUIPO = int(meta_global * pct_equipo)
        
        # ================================================================
        # PASO 2: Contratos del Equipo
        # ================================================================
        debug_log.append(f"Query 2: Contratos equipo {'año' if month == 'all' else 'mes'}")
        
        sql_contratos_equipo = '''
            SELECT COUNT(DISTINCT lead_id) as contratos_mes
            FROM bi_DimLeads
            WHERE YEAR(contrato_created_at) = %s 
              AND corredor_id IN (
                  SELECT corredor_id FROM bi_DimCorredores 
                  WHERE coordinador = %s AND activo = 1
              )
        '''
        params_contratos = [use_year, coordinador_email]
        if month != 'all':
            sql_contratos_equipo += ' AND MONTH(contrato_created_at) = %s'
            params_contratos.append(use_month)
            
        cursor.execute(sql_contratos_equipo, tuple(params_contratos))
        contratos_equipo_actual = int(cursor.fetchone()['contratos_mes'] or 0)
        
        # ================================================================
        # PASO 3: Data Individual Base (Contratos, Leads, Prospectos)
        # ================================================================
        debug_log.append(f"Query 3: Data individual base {'año' if month == 'all' else 'mes'}")
        
        sql_base = '''
            SELECT 
                c.corredor_id,
                c.nombre_corredor,
                COALESCE(NULLIF(c.reserva, 0), 7) as reservas_historicas,
                COALESCE(l.contratos_periodo, 0) as contratos_periodo,
                COALESCE(l.leads_tomados_periodo, 0) as leads_tomados_periodo,
                COALESCE(l.prospectos_periodo, 0) as prospectos_periodo,
                COALESCE(l.leads_descartados_sin_gestion, 0) as leads_descartados,
                COALESCE(l.prospectos_descartados, 0) as prospectos_descartados,
                COALESCE(l.contacto_24h, 0) as contacto_24h
            FROM bi_DimCorredores c
            LEFT JOIN (
                SELECT 
                    corredor_id,
                    COUNT(DISTINCT CASE WHEN contrato_created_at IS NOT NULL THEN lead_id END) as contratos_periodo,
                    COUNT(DISTINCT lead_id) as leads_tomados_periodo,
                    COUNT(DISTINCT CASE WHEN step_3_prospecto = 1 THEN lead_id END) as prospectos_periodo,
                    SUM(CASE WHEN step_1_epc_descartado = 1 AND lag_contacto IS NULL THEN 1 ELSE 0 END) as leads_descartados_sin_gestion,
                    SUM(CASE WHEN step_3_prospecto_descartado = 1 THEN 1 ELSE 0 END) as prospectos_descartados,
                    SUM(CASE WHEN lag_contacto IS NOT NULL AND lag_contacto <= 24 THEN 1 ELSE 0 END) as contacto_24h
                FROM bi_DimLeads
                WHERE YEAR(fecha_tomado) = %s 
        '''
        params_base = [use_year]
        if month != 'all':
            sql_base += ' AND MONTH(fecha_tomado) = %s'
            params_base.append(use_month)
            
        sql_base += '''
                GROUP BY corredor_id
            ) l ON c.corredor_id = l.corredor_id
            WHERE c.coordinador = %s 
              AND c.activo = 1
            ORDER BY contratos_periodo DESC, c.reserva DESC
        '''
        params_base.append(coordinador_email)
        
        cursor.execute(sql_base, tuple(params_base))
        corredores_data = cursor.fetchall()
        
        # ================================================================
        # PASO 4: Visitas (Agendas)
        # ================================================================
        debug_log.append(f"Query 4: Visitas {'año' if month == 'all' else 'mes'}")
        sql_visitas = '''
            SELECT 
                corredor_id,
                COUNT(*) as total_agendas,
                SUM(CASE WHEN estado = 'Visitado' THEN 1 ELSE 0 END) as visitas_realizadas,
                SUM(CASE WHEN estado = 'Cancelado' THEN 1 ELSE 0 END) as visitas_canceladas
            FROM bi_DimAgendas
            WHERE YEAR(agenda_fecha) = %s 
        '''
        params_visitas = [use_year]
        if month != 'all':
            sql_visitas += ' AND MONTH(agenda_fecha) = %s'
            params_visitas.append(use_month)
            
        sql_visitas += '''
            AND corredor_id IS NOT NULL
            GROUP BY corredor_id
        '''
        
        cursor.execute(sql_visitas, tuple(params_visitas))
        visit_metrics = {str(row['corredor_id']): row for row in cursor.fetchall()}
        
        # ================================================================
        # PASO 5: Calcular métricas RAW para cada corredor
        # ================================================================
        debug_log.append("Calculating raw metrics...")
        dias_restantes = calculate_dias_restantes(year=use_year, month=use_month) if month != 'all' else 0
        brokers_raw = []
        
        for corredor in corredores_data:
            corredor_id = str(corredor['corredor_id'])
            
            # Meta personalizada
            reservas_hist = float(corredor['reservas_historicas'] or 0)
            pct_corredor = reservas_hist / total_equipo_hist if total_equipo_hist > 0 else 0
            meta_corredor = int(META_EQUIPO * pct_corredor)
            
            # Conversiones periodo
            contratos_periodo = int(corredor['contratos_periodo'] or 0)
            leads_periodo = int(corredor['leads_tomados_periodo'] or 0)
            prospectos_periodo = int(corredor['prospectos_periodo'] or 0)
            leads_descartados = int(corredor['leads_descartados'] or 0)
            prospectos_descartados = int(corredor['prospectos_descartados'] or 0)
            contacto_24h = int(corredor['contacto_24h'] or 0)

            # Visitas
            visit_data = visit_metrics.get(corredor_id, {})
            total_agendas = int(visit_data.get('total_agendas', 0) or 1)
            visitas_realizadas = int(visit_data.get('visitas_realizadas', 0) or 0)
            visitas_canceladas = int(visit_data.get('visitas_canceladas', 0) or 0)

            # === ENGAGEMENT METRICS (RAW) ===
            tasa_visitas = calculate_rate_with_smoothing(visitas_realizadas, total_agendas, 15)
            tasa_no_cancela = 1 - calculate_rate_with_smoothing(visitas_canceladas, total_agendas, 15)
            tasa_no_descarta_leads = 1 - calculate_rate_with_smoothing(leads_descartados, leads_periodo, 15)
            tasa_no_descarta_prospectos = 1 - calculate_rate_with_smoothing(prospectos_descartados, prospectos_periodo, 15)
            tasa_contacto_24h = calculate_rate_with_smoothing(contacto_24h, leads_periodo, 15)

            # === RENDIMIENTO METRICS (RAW) ===
            conv_prospecto_contrato = calculate_rate_with_smoothing(contratos_periodo, prospectos_periodo, 15)
            conv_lead_contrato = calculate_rate_with_smoothing(contratos_periodo, leads_periodo, 15)
            contratos_absolutos = contratos_periodo
            leads_por_visita = calculate_rate_with_smoothing(leads_periodo, visitas_realizadas, 0) if visitas_realizadas > 0 else 0

            # === EFICIENCIA METRICS (RAW) ===
            tasa_demora = 1 - calculate_rate_with_smoothing(contacto_24h, leads_periodo, 15)
            tiempo_normalizado = 0.5 # Default
            tickets_normalizado = 0.0 # Default

            # === Datos Operativos ===
            faltante = max(meta_corredor - contratos_periodo, 0)
            conv_periodo = (prospectos_periodo / leads_periodo * 100) if leads_periodo > 0 else 0
            
            leads_diarios_necesarios = int((faltante / max(dias_restantes, 1)) / (conv_periodo / 100)) if conv_periodo > 0 and dias_restantes > 0 else 0

            brokers_raw.append({
                'corredor_id': corredor_id,
                'nombre': corredor['nombre_corredor'],
                'meta_personal': meta_corredor,
                'contratos_periodo': contratos_periodo,
                'faltante': faltante,
                'leads_periodo': leads_periodo,
                'prospectos_periodo': prospectos_periodo,
                'conversion': f"{conv_periodo:.1f}",
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
                'leads_por_visita': leads_por_visita,
                # Eficiencia
                'tasa_demora': tasa_demora,
                'tiempo_normalizado': tiempo_normalizado,
                'tickets_normalizado': tickets_normalizado
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

        all_tasa_demora = [b['tasa_demora'] for b in brokers_raw]

        # Normalizar
        norm_tasa_visitas = normalize_z_score_simple(all_tasa_visitas)
        norm_tasa_no_cancela = normalize_z_score_simple(all_tasa_no_cancela)
        norm_tasa_no_descarta_leads = normalize_z_score_simple(all_tasa_no_descarta_leads)
        norm_tasa_no_descarta_prospectos = normalize_z_score_simple(all_tasa_no_descarta_prospectos)
        norm_tasa_contacto_24h = normalize_z_score_simple(all_tasa_contacto_24h)

        norm_conv_p_c = normalize_z_score_simple(all_conv_p_c)
        norm_conv_l_c = normalize_z_score_simple(all_conv_l_c)
        norm_contratos_abs = normalize_z_score_simple(all_contratos_abs)
        norm_lpv = normalize_z_score_simple(all_lpv)

        norm_tasa_demora = normalize_z_score_simple(all_tasa_demora, inverse=True)

        # ================================================================
        # PASO 7: CALCULAR SCORES FINALES (100 pts) - MODELO V4 PRIORIZADO
        # ================================================================
        debug_log.append("Calculating scores (Scoring Model V4: 30/55/15)...")
        brokers_final = []
        
        for i, broker_raw in enumerate(brokers_raw):
            # ENGAGEMENT (30 pts total - antes 35)
            # Bajamos el peso individual de 7 a 6
            eng_visitas = norm_tasa_visitas[i] * 6
            eng_no_cancela = norm_tasa_no_cancela[i] * 6
            eng_no_descarta_leads = norm_tasa_no_descarta_leads[i] * 6
            eng_no_descarta_prospectos = norm_tasa_no_descarta_prospectos[i] * 6
            eng_contacto_24h = norm_tasa_contacto_24h[i] * 6
            engagement_score = eng_visitas + eng_no_cancela + eng_no_descarta_leads + eng_no_descarta_prospectos + eng_contacto_24h
            
            # RENDIMIENTO (55 pts total - antes 40)
            # Subimos el peso de conversión y contratos absolutos de 10 a 13.75
            rend_conv_p_c = norm_conv_p_c[i] * 13.75
            rend_conv_l_c = norm_conv_l_c[i] * 13.75
            rend_contratos_abs = norm_contratos_abs[i] * 13.75
            rend_lpv = norm_lpv[i] * 13.75
            rendimiento_score = rend_conv_p_c + rend_conv_l_c + rend_contratos_abs + rend_lpv
            
            # EFICIENCIA (15 pts total - antes 25)
            efi_demora = norm_tasa_demora[i] * 5
            efi_tiempo = 0.5 * 5
            efi_tickets = 1.0 * 5
            eficiencia_score = efi_demora + efi_tiempo + efi_tickets

            # TOTAL (100 pts)
            total_score = engagement_score + rendimiento_score + eficiencia_score
            
            # Acción Sugerida
            if broker_raw['contratos_periodo'] >= broker_raw['meta_personal']:
                action = "¡Meta Cumplida!"
            elif broker_raw['leads_diarios_necesarios'] > 0:
                action = f"Asignar {broker_raw['leads_diarios_necesarios']} leads/día"
            elif month == 'all':
                action = "Mantener Ritmo Anual"
            else:
                action = "Revisar Conversión"
            
            brokers_final.append({
                "name": broker_raw['nombre'],
                "leads": broker_raw['leads_periodo'],
                "reservas": broker_raw['contratos_periodo'],
                "meta_personal": broker_raw['meta_personal'],
                "faltante": broker_raw['faltante'],
                "conversion": broker_raw['conversion'],
                "leadsNeeded": broker_raw['leads_diarios_necesarios'],
                "action": action,
                "score": round(total_score, 2),
                "score_engagement": round(engagement_score, 2),
                "score_rendimiento": round(rendimiento_score, 2),
                "score_eficiencia": round(eficiencia_score, 2),
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
                },
                "breakdown_eficiencia": {
                    "sin_demora": round(efi_demora, 2),
                    "tiempo_resolucion": round(efi_tiempo, 2),
                    "tickets_severidad": round(efi_tickets, 2)
                }
            })
        
        cursor.close()
        conn.close()
        
        return {
            "brokers": brokers_final,
            "squad_summary": {
                "meta_equipo": META_EQUIPO,
                "contratos_actuales": contratos_equipo_actual,
                "faltante_equipo": max(META_EQUIPO - contratos_equipo_actual, 0),
                "dias_restantes": dias_restantes,
                "debug_log": debug_log,
                "scoring_version": "Model V4 - Rendimiento (55%) > Engagement (30%) > Eficiencia (15%)"
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
            from urllib.parse import parse_qs, urlparse
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            coordinator = query_params.get('coordinator', ['carlos.echeverria'])[0]
            year = query_params.get('year', [None])[0]
            month = query_params.get('month', [None])[0]

            data = fetch_squad_intelligence(coordinator, year=year, month=month)
            
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
