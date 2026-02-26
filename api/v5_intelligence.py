from http.server import BaseHTTPRequestHandler
import json
import mysql.connector
import os
from datetime import datetime, date
import calendar
import statistics
import math

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
META_GLOBAL_110 = 1707  # Meta total mensual (110%)
CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month  # Dinámico - mes actual

# Comunas de Región Metropolitana (RM)
RM_COMUNAS = {
    'Santiago', 'Estación Central', 'Independencia', 'La Cisterna', 
    'La Florida', 'Las Condes', 'Macul', 'Ñuñoa', 'Providencia', 
    'Quinta Normal', 'San Joaquín', 'San Miguel', 'Vitacura', 'Renca',
    'Cerrillos', 'Huechuraba', 'La Granja', 'Maipú', 'Recoleta',
    'Pedro Aguirre Cerda', 'La Reina', 'Peñalolén', 'San Ramón',
    'El Bosque', 'Conchalí', 'Lo Espejo', 'Pudahuel', 'Quilicura',
    'Lo Prado', 'La Pintana', 'San José de Maipo', 'Padre Hurtado',
    'Pirque', 'Peñaflor', 'Talagante', 'Buin', 'Paine', 'Colina',
    'Lampa', 'Tiltil', 'Curacaví', 'María Pinto', 'El Monte',
    'Isla de Maipo', 'Calera de Tango', 'San Bernardo', 'Puente Alto'
}

# Comunas de Regiones (fuera de RM)
REGIONES_COMUNAS = {
    'Valparaíso', 'Villa Alemana', 'Viña Del Mar', 'Concón', 'Quilpué',
    'Rancagua', 'Machalí', 'Requínoa',
    'Temuco', 'Padre Las Casas', 'Villarrica', 'Pucón',
    'Coquimbo', 'La Serena', 'Ovalle',
    'Concepción', 'Talcahuano', 'Chillán', 'Los Ángeles',
    'Calama', 'Antofagasta', 'Copiapó',
    'Iquique', 'Arica', 'Osorno', 'Puerto Montt', 'Valdivia',
    'Talca', 'Curicó', 'Linares', 'Cauquenes'
}

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
# CLASIFICACIÓN REGIONAL
# ===================================================================
def classify_broker_region(comunas_list):
    """
    Clasifica un corredor como RM o REGIONES basado en las comunas donde opera.
    Si opera en al menos una comuna de regiones, se considera REGIONES.
    """
    if not comunas_list:
        return 'RM'  # Default
    
    comunas_set = set(comunas_list)
    
    # Si tiene alguna comuna de regiones, es REGIONES
    if comunas_set & REGIONES_COMUNAS:
        return 'REGIONES'
    
    # Si solo tiene comunas de RM, es RM
    if comunas_set & RM_COMUNAS:
        return 'RM'
    
    return 'RM'  # Default

def get_robust_mean_std(values):
    """
    Calcula media y desviación estándar robustas usando IQR para detectar outliers.
    Los outliers se truncan a ±3 IQR antes de calcular estadísticos.
    """
    if not values or len(values) < 2:
        return statistics.mean(values) if values else 0, 1.0
    
    # Calcular Q1, Q3, IQR
    sorted_values = sorted(values)
    n = len(sorted_values)
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    q1 = sorted_values[q1_idx]
    q3 = sorted_values[q3_idx]
    iqr = q3 - q1
    
    # Límites para outliers
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # Truncar outliers
    truncated = [max(lower_bound, min(v, upper_bound)) for v in values]
    
    # Calcular estadísticos con datos truncados
    mean = statistics.mean(truncated)
    stdev = statistics.stdev(truncated) if len(truncated) > 1 else 1.0
    
    return mean, max(stdev, 0.001)  # Evitar stdev = 0

def normalize_z_score_robust(values, inverse=False):
    """
    Normaliza valores usando z-score robusto con transformación sigmoide.
    Usa media y stdev robustas (truncando outliers).
    Retorna valores entre 0 y 1.
    
    Args:
        values: Lista de valores a normalizar
        inverse: Si True, invierte la escala (para métricas donde menor es mejor)
    """
    if not values or len(values) < 2:
        return [0.5] * len(values)
    
    mean, stdev = get_robust_mean_std(values)
    
    if stdev == 0:
        return [0.5] * len(values)
    
    # Calcular Z-scores
    z_scores = [(v - mean) / stdev for v in values]
    
    # Transformación sigmoide: mapea Z a (0, 1)
    # Usamos tanh(x/2) que es más suave que sigmoid para valores extremos
    normalized = [(math.tanh(z / 2) + 1) / 2 for z in z_scores]
    
    if inverse:
        normalized = [1 - n for n in normalized]
    
    return normalized

def calculate_percentile_rank(value, values):
    """
    Calcula el percentil de un valor dentro de una distribución.
    Retorna valor entre 0 y 100.
    """
    if not values:
        return 50
    
    sorted_values = sorted(values)
    count_below = sum(1 for v in sorted_values if v < value)
    percentile = (count_below / len(sorted_values)) * 100
    return min(100, max(0, percentile))

def fetch_squad_intelligence_v5(coordinador_email="carlos.echeverria", filter_region="ALL"):
    """
    Sistema de Inteligencia con Scoring Estadístico Robusto - Fase 3
    Enfocado en RM con diferenciación clara de Regiones.
    
    Scoring con 4 Pilares:
    1. Engagement & Gestión Activa (35%): Seriedad del corredor con el proceso
       - % visitas realizadas / agendadas
       - % visitas canceladas (penaliza)
       - % leads descartados por no gestión
       - % prospectos descartados por no gestión
       - % leads con al menos 1 acción dentro de X horas
    
    2. Rendimiento & Conversión (40%):
       - Eficacia: % prospecto→reserva/contrato, % lead→reserva/contrato
       - Capacidad productiva: Contratos/reservas (absoluto), Leads/visitas
    
    3. Eficiencia Operativa y Tiempos (25%):
       - % prospectos con demora en Ingreso/Observación/Aprobación
       - Tiempo prom de resolución
       - Tickets de soporte ponderados por severidad
    
    Args:
        coordinador_email: Email del coordinador
        filter_region: 'ALL', 'RM', o 'REGIONES'
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
        # PASO 3: Data Individual Base con Comunas, Métricas de Tiempo y Teléfono (desde Zendesk)
        # ================================================================
        debug_log.append("Query 3: Data individual base con comunas, tiempos y telefono")
        cursor.execute('''
            SELECT
                c.corredor_id,
                c.nombre_corredor,
                COALESCE(NULLIF(c.reserva, 0), 7) as reservas_historicas,
                COALESCE(l.contratos_mes, 0) as contratos_mes,
                COALESCE(l.leads_tomados_mes, 0) as leads_tomados_mes,
                COALESCE(l.prospectos_mes, 0) as prospectos_mes,
                COALESCE(l.leads_descartados_sin_gestion, 0) as leads_descartados,
                COALESCE(l.prospectos_descartados, 0) as prospectos_descartados,
                COALESCE(l.contacto_24h, 0) as contacto_24h,
                COALESCE(l.accion_24h, 0) as accion_24h,
                0 as tiempo_prom_resolucion,
                0 as tickets_severidad,
                0 as prospectos_demora,
                NULL as comunas,
                NULL as telefono
            FROM bi_DimCorredores c
            LEFT JOIN (
                SELECT
                    corredor_id,
                    COUNT(DISTINCT CASE WHEN contrato_created_at IS NOT NULL THEN lead_id END) as contratos_mes,
                    COUNT(DISTINCT lead_id) as leads_tomados_mes,
                    COUNT(DISTINCT CASE WHEN step_3_prospecto = 1 THEN lead_id END) as prospectos_mes,
                    SUM(CASE WHEN step_1_epc_descartado = 1 AND lag_contacto IS NULL THEN 1 ELSE 0 END) as leads_descartados_sin_gestion,
                    SUM(CASE WHEN step_3_prospecto_descartado = 1 THEN 1 ELSE 0 END) as prospectos_descartados,
                    SUM(CASE WHEN lag_contacto IS NOT NULL AND lag_contacto <= 24 THEN 1 ELSE 0 END) as contacto_24h,
                    SUM(CASE WHEN lag_contacto IS NOT NULL AND lag_contacto <= 24 THEN 1 ELSE 0 END) as accion_24h
                FROM bi_DimLeads
                WHERE YEAR(fecha_tomado) = %s
                  AND MONTH(fecha_tomado) = %s
                GROUP BY corredor_id
            ) l ON c.corredor_id = l.corredor_id
            LEFT JOIN bi_DimAgendas a ON c.corredor_id = a.corredor_id
                AND YEAR(a.agenda_fecha) = %s
                AND MONTH(a.agenda_fecha) = %s
            WHERE c.coordinador = %s
              AND c.activo = 1
            GROUP BY c.corredor_id, c.nombre_corredor, c.reserva,
                     l.contratos_mes, l.leads_tomados_mes, l.prospectos_mes,
                     l.leads_descartados_sin_gestion, l.prospectos_descartados, l.contacto_24h,
                     l.accion_24h
            ORDER BY contratos_mes DESC, c.reserva DESC
        ''', (CURRENT_YEAR, CURRENT_MONTH, CURRENT_YEAR, CURRENT_MONTH, coordinador_email))
        
        corredores_data = cursor.fetchall()
        
        # ================================================================
        # PASO 4: Visitas (Agendas) con detalle
        # ================================================================
        debug_log.append("Query 4: Visitas mes")
        cursor.execute('''
            SELECT
                corredor_id,
                COUNT(*) as total_agendas,
                SUM(CASE WHEN estado = 'Visitado' THEN 1 ELSE 0 END) as visitas_realizadas,
                SUM(CASE WHEN estado = 'Cancelado' THEN 1 ELSE 0 END) as visitas_canceladas,
                SUM(CASE WHEN estado = 'No Contestó' THEN 1 ELSE 0 END) as no_contesto
            FROM bi_DimAgendas
            WHERE YEAR(agenda_fecha) = %s
              AND MONTH(agenda_fecha) = %s
              AND corredor_id IS NOT NULL
            GROUP BY corredor_id
        ''', (CURRENT_YEAR, CURRENT_MONTH))
        
        visit_metrics = {str(row['corredor_id']): row for row in cursor.fetchall()}
        
        # ================================================================
        # PASO 5: Clasificar corredores por región
        # ================================================================
        debug_log.append("Classifying brokers by region...")
        dias_restantes = calculate_dias_restantes()
        brokers_rm = []
        brokers_regiones = []
        
        for corredor in corredores_data:
            corredor_id = str(corredor['corredor_id'])
            comunas_str = corredor['comunas'] or ''
            comunas_list = [c.strip() for c in comunas_str.split(',') if c.strip()]
            
            region_type = classify_broker_region(comunas_list)
            
            # Meta personalizada
            reservas_hist = float(corredor['reservas_historicas'] or 0)
            pct_corredor = reservas_hist / total_equipo_hist if total_equipo_hist > 0 else 0
            meta_corredor = int(META_EQUIPO * pct_corredor)
            
            # Conversiones
            contratos_mes = int(corredor['contratos_mes'] or 0)
            leads_mes = int(corredor['leads_tomados_mes'] or 0)
            prospectos_mes = int(corredor['prospectos_mes'] or 0)
            leads_descartados = int(corredor['leads_descartados'] or 0)
            prospectos_descartados = int(corredor['prospectos_descartados'] or 0)
            contacto_24h = int(corredor['contacto_24h'] or 0)
            accion_24h = int(corredor['accion_24h'] or 0)
            
            # Eficiencia operativa
            tiempo_prom_resolucion = float(corredor['tiempo_prom_resolucion'] or 0)
            tickets_severidad = float(corredor['tickets_severidad'] or 0)
            prospectos_demora = int(corredor['prospectos_demora'] or 0)
            
            # Visitas
            visit_data = visit_metrics.get(corredor_id, {})
            total_agendas = int(visit_data.get('total_agendas', 0) or 1)
            visitas_realizadas = int(visit_data.get('visitas_realizadas', 0) or 0)
            visitas_canceladas = int(visit_data.get('visitas_canceladas', 0) or 0)
            no_contesto = int(visit_data.get('no_contesto', 0) or 0)
            
            # === ENGAGEMENT METRICS (RAW) - Pilar 1 (35%) ===
            # % visitas realizadas / agendadas
            tasa_visitas = visitas_realizadas / total_agendas if total_agendas > 0 else 0
            # % visitas canceladas (penaliza - inversa)
            tasa_cancelacion = visitas_canceladas / total_agendas if total_agendas > 0 else 0
            # % leads descartados por no gestión
            tasa_descarte_leads = leads_descartados / leads_mes if leads_mes > 0 else 0
            # % prospectos descartados por no gestión
            tasa_descarte_prospectos = prospectos_descartados / prospectos_mes if prospectos_mes > 0 else 0
            # % leads con al menos 1 acción dentro de 24h
            tasa_accion_24h = accion_24h / leads_mes if leads_mes > 0 else 0
            
            # === RENDIMIENTO METRICS (RAW) - Pilar 2 (40%) ===
            # Eficacia
            conv_prospecto_contrato = contratos_mes / prospectos_mes if prospectos_mes > 0 else 0
            conv_lead_contrato = contratos_mes / leads_mes if leads_mes > 0 else 0
            # Capacidad productiva (valores absolutos y tasas)
            contratos_absolutos = contratos_mes  # Valor absoluto
            leads_por_visita = leads_mes / visitas_realizadas if visitas_realizadas > 0 else 0
            
            # === EFICIENCIA OPERATIVA (RAW) - Pilar 3 (25%) ===
            # % prospectos con demora (inversa - menor es mejor)
            tasa_demora = prospectos_demora / prospectos_mes if prospectos_mes > 0 else 0
            # Tiempo promedio de resolución (inverso - menor es mejor)
            # Normalizar a horas, asumir max 72h como peor caso
            tiempo_normalizado = min(tiempo_prom_resolucion / 72, 1) if tiempo_prom_resolucion > 0 else 0
            # Tickets severidad (inverso - menor es mejor)
            # Normalizar (asumir max 30 puntos como peor caso)
            tickets_normalizado = min(tickets_severidad / 30, 1) if tickets_severidad > 0 else 0
            
            # === Datos Operativos ===
            faltante = max(meta_corredor - contratos_mes, 0)
            conv_mes = (prospectos_mes / leads_mes * 100) if leads_mes > 0 else 0
            leads_diarios_necesarios = int((faltante / dias_restantes) / (conv_mes / 100)) if conv_mes > 0 else 0
            
            broker_data = {
                'corredor_id': corredor_id,
                'nombre': corredor['nombre_corredor'],
                'region_type': region_type,
                'comunas': comunas_list,
                'meta_personal': meta_corredor,
                'contratos_mes': contratos_mes,
                'faltante': faltante,
                'leads_mes': leads_mes,
                'prospectos_mes': prospectos_mes,
                'conversion': f"{conv_mes:.1f}",
                'visitas_realizadas': visitas_realizadas,
                'visitas_canceladas': visitas_canceladas,
                'no_contesto': no_contesto,
                'leads_diarios_necesarios': leads_diarios_necesarios,
                'telefono': corredor.get('telefono'),  # Teléfono desde bi_DimLeads
                # Métricas RAW Engagement (Pilar 1)
                'tasa_visitas': tasa_visitas,
                'tasa_cancelacion': tasa_cancelacion,
                'tasa_descarte_leads': tasa_descarte_leads,
                'tasa_descarte_prospectos': tasa_descarte_prospectos,
                'tasa_accion_24h': tasa_accion_24h,
                # Métricas RAW Rendimiento (Pilar 2)
                'conv_prospecto_contrato': conv_prospecto_contrato,
                'conv_lead_contrato': conv_lead_contrato,
                'contratos_absolutos': contratos_absolutos,
                'leads_por_visita': leads_por_visita,
                # Métricas RAW Eficiencia (Pilar 3)
                'tasa_demora': tasa_demora,
                'tiempo_normalizado': tiempo_normalizado,
                'tickets_normalizado': tickets_normalizado
            }
            
            if region_type == 'RM':
                brokers_rm.append(broker_data)
            else:
                brokers_regiones.append(broker_data)
        
        # ================================================================
        # PASO 6: Filtrar por región si se especifica
        # ================================================================
        if filter_region == 'RM':
            brokers_to_score = brokers_rm
        elif filter_region == 'REGIONES':
            brokers_to_score = brokers_regiones
        else:
            brokers_to_score = brokers_rm + brokers_regiones
        
        # Si no hay datos, retornar vacío
        if not brokers_to_score:
            return {
                "brokers": [],
                "brokers_rm": [],
                "brokers_regiones": [],
                "squad_summary": {
                    "meta_equipo": META_EQUIPO,
                    "contratos_actuales": contratos_equipo_mes,
                    "total_brokers_rm": len(brokers_rm),
                    "total_brokers_regiones": len(brokers_regiones)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # ================================================================
        # PASO 7: NORMALIZACIÓN Z-SCORE ROBUSTO DE MÉTRICAS
        # ================================================================
        debug_log.append("Normalizing metrics with robust Z-score...")
        
        # Extraer métricas para normalización - PILAR 1: Engagement (35%)
        all_tasa_visitas = [b['tasa_visitas'] for b in brokers_to_score]
        all_tasa_cancelacion = [b['tasa_cancelacion'] for b in brokers_to_score]  # Inversa
        all_tasa_descarte_leads = [b['tasa_descarte_leads'] for b in brokers_to_score]  # Inversa
        all_tasa_descarte_prospectos = [b['tasa_descarte_prospectos'] for b in brokers_to_score]  # Inversa
        all_tasa_accion_24h = [b['tasa_accion_24h'] for b in brokers_to_score]
        
        # Extraer métricas - PILAR 2: Rendimiento (40%)
        all_conv_p_c = [b['conv_prospecto_contrato'] for b in brokers_to_score]
        all_conv_l_c = [b['conv_lead_contrato'] for b in brokers_to_score]
        all_contratos_abs = [b['contratos_absolutos'] for b in brokers_to_score]
        all_lpv = [b['leads_por_visita'] for b in brokers_to_score]
        
        # Extraer métricas - PILAR 3: Eficiencia (25%)
        all_tasa_demora = [b['tasa_demora'] for b in brokers_to_score]  # Inversa
        all_tiempo_norm = [b['tiempo_normalizado'] for b in brokers_to_score]  # Inverso
        all_tickets_norm = [b['tickets_normalizado'] for b in brokers_to_score]  # Inverso
        
        # Normalizar PILAR 1: Engagement (35%)
        # Las inversas se normalizan con inverse=True
        norm_tasa_visitas = normalize_z_score_robust(all_tasa_visitas, inverse=False)
        norm_tasa_cancelacion = normalize_z_score_robust(all_tasa_cancelacion, inverse=True)
        norm_tasa_descarte_leads = normalize_z_score_robust(all_tasa_descarte_leads, inverse=True)
        norm_tasa_descarte_prospectos = normalize_z_score_robust(all_tasa_descarte_prospectos, inverse=True)
        norm_tasa_accion_24h = normalize_z_score_robust(all_tasa_accion_24h, inverse=False)
        
        # Normalizar PILAR 2: Rendimiento (40%)
        norm_conv_p_c = normalize_z_score_robust(all_conv_p_c)
        norm_conv_l_c = normalize_z_score_robust(all_conv_l_c)
        norm_contratos_abs = normalize_z_score_robust(all_contratos_abs)
        norm_lpv = normalize_z_score_robust(all_lpv)
        
        # Normalizar PILAR 3: Eficiencia (25%) - todas inversas
        norm_tasa_demora = normalize_z_score_robust(all_tasa_demora, inverse=True)
        norm_tiempo_norm = normalize_z_score_robust(all_tiempo_norm, inverse=True)
        norm_tickets_norm = normalize_z_score_robust(all_tickets_norm, inverse=True)
        
        # ================================================================
        # PASO 8: CALCULAR SCORES FINALES CON 3 PILARES
        # ================================================================
        debug_log.append("Calculating final scores with 3 pillars...")
        brokers_final = []
        
        for i, broker in enumerate(brokers_to_score):
            # ============================================
            # PILAR 1: ENGAGEMENT & GESTIÓN ACTIVA (35%)
            # ============================================
            # % visitas realizadas / agendadas (20% del pilar = 7% del total)
            eng_visitas = norm_tasa_visitas[i] * 7
            # % visitas no canceladas (20% del pilar = 7% del total)
            eng_no_cancela = norm_tasa_cancelacion[i] * 7
            # % leads NO descartados (20% del pilar = 7% del total)
            eng_no_descarta_leads = norm_tasa_descarte_leads[i] * 7
            # % prospectos NO descartados (20% del pilar = 7% del total)
            eng_no_descarta_prospectos = norm_tasa_descarte_prospectos[i] * 7
            # % leads con acción 24h (20% del pilar = 7% del total)
            eng_accion_24h = norm_tasa_accion_24h[i] * 7
            
            engagement_score = eng_visitas + eng_no_cancela + eng_no_descarta_leads + eng_no_descarta_prospectos + eng_accion_24h
            
            # ============================================
            # PILAR 2: RENDIMIENTO & CONVERSIÓN (40%)
            # ============================================
            # Eficacia (50% del pilar = 20% del total)
            rend_conv_p_c = norm_conv_p_c[i] * 10  # % prospecto→contrato
            rend_conv_l_c = norm_conv_l_c[i] * 10  # % lead→contrato
            
            # Capacidad productiva (50% del pilar = 20% del total)
            rend_contratos_abs = norm_contratos_abs[i] * 10  # Contratos absolutos
            rend_lpv = norm_lpv[i] * 10  # Leads/visita
            
            rendimiento_score = rend_conv_p_c + rend_conv_l_c + rend_contratos_abs + rend_lpv
            
            # ============================================
            # PILAR 3: EFICIENCIA OPERATIVA Y TIEMPOS (25%)
            # ============================================
            # % prospectos SIN demora (33% del pilar = 8.25% del total)
            efi_demora = norm_tasa_demora[i] * 8.25
            # Tiempo de resolución (33% del pilar = 8.25% del total)
            efi_tiempo = norm_tiempo_norm[i] * 8.25
            # Tickets severidad (34% del pilar = 8.5% del total)
            efi_tickets = norm_tickets_norm[i] * 8.5
            
            eficiencia_score = efi_demora + efi_tiempo + efi_tickets
            
            # ============================================
            # SCORE TOTAL (100 pts)
            # ============================================
            total_score = engagement_score + rendimiento_score + eficiencia_score
            
            # Calcular percentil para ranking
            all_scores = [b['contratos_mes'] for b in brokers_to_score]
            percentile = calculate_percentile_rank(broker['contratos_mes'], all_scores)
            
            # Acción Sugerida
            if broker['contratos_mes'] >= broker['meta_personal']:
                action = "¡Meta Cumplida!"
            elif broker['leads_diarios_necesarios'] > 20:
                action = "Coaching Urgente"
            elif broker['leads_diarios_necesarios'] > 0:
                action = f"Asignar {broker['leads_diarios_necesarios']} leads/día"
            else:
                action = "Revisar Conversión"
            
            brokers_final.append({
                "name": broker['nombre'],
                "region_type": broker['region_type'],
                "comunas": broker['comunas'][:5] if len(broker['comunas']) > 5 else broker['comunas'],
                "leads": broker['leads_mes'],
                "reservas": broker['contratos_mes'],
                "meta_personal": broker['meta_personal'],
                "faltante": broker['faltante'],
                "conversion": broker['conversion'],
                "leadsNeeded": broker['leads_diarios_necesarios'],
                "action": action,
                "score": round(total_score, 2),
                "percentile": round(percentile, 1),
                "score_engagement": round(engagement_score, 2),
                "score_rendimiento": round(rendimiento_score, 2),
                "score_eficiencia": round(eficiencia_score, 2),
                "visitas_realizadas": broker['visitas_realizadas'],
                "visitas_canceladas": broker['visitas_canceladas'],
                "no_contesto": broker['no_contesto'],
                "telefono": broker.get('telefono'),  # Teléfono para WhatsApp
                "breakdown_engagement": {
                    "visitas_realizadas": round(eng_visitas, 2),
                    "visitas_no_canceladas": round(eng_no_cancela, 2),
                    "leads_no_descartados": round(eng_no_descarta_leads, 2),
                    "prospectos_no_descartados": round(eng_no_descarta_prospectos, 2),
                    "accion_24h": round(eng_accion_24h, 2)
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
        
        # Ordenar por score descendente
        brokers_final.sort(key=lambda x: x['score'], reverse=True)
        
        # Identificar líder de performance
        leader = brokers_final[0] if brokers_final else None
        
        cursor.close()
        conn.close()
        
        return {
            "brokers": brokers_final,
            "brokers_rm": [b for b in brokers_final if b['region_type'] == 'RM'],
            "brokers_regiones": [b for b in brokers_final if b['region_type'] == 'REGIONES'],
            "leader": leader,
            "squad_summary": {
                "meta_equipo": META_EQUIPO,
                "contratos_actuales": contratos_equipo_mes,
                "faltante_equipo": max(META_EQUIPO - contratos_equipo_mes, 0),
                "dias_restantes": dias_restantes,
                "total_brokers_rm": len(brokers_rm),
                "total_brokers_regiones": len(brokers_regiones),
                "debug_log": debug_log,
                "scoring_version": "Phase 3 - 3 Pilares (Engagement 35% + Rendimiento 40% + Eficiencia 25%)",
                "scoring_methodology": {
                    "pilar_1_engagement": {
                        "weight": 35,
                        "metrics": [
                            "visitas_realizadas_agendadas",
                            "visitas_no_canceladas",
                            "leads_no_descartados",
                            "prospectos_no_descartados",
                            "accion_24h"
                        ]
                    },
                    "pilar_2_rendimiento": {
                        "weight": 40,
                        "metrics": [
                            "conv_prospecto_contrato",
                            "conv_lead_contrato",
                            "contratos_absolutos",
                            "leads_por_visita"
                        ]
                    },
                    "pilar_3_eficiencia": {
                        "weight": 25,
                        "metrics": [
                            "sin_demora",
                            "tiempo_resolucion",
                            "tickets_severidad"
                        ]
                    },
                    "total_possible": 100,
                    "normalization": "Robust Z-Score with IQR truncation"
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        import traceback
        traceback.print_exc()
        return {"error": str(e), "debug_log": debug_log}

# ===================================================================
# VERCEL SERVERLESS HANDLER
# ===================================================================
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Endpoint: GET /api/v5_intelligence
        Query params:
          - coordinator: email del coordinador (default: carlos.echeverria)
          - region: 'ALL', 'RM', o 'REGIONES' (default: 'ALL')
        """
        try:
            from urllib.parse import parse_qs, urlparse
            
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            coordinator = query_params.get('coordinator', ['carlos.echeverria'])[0]
            region = query_params.get('region', ['ALL'])[0]
            
            data = fetch_squad_intelligence_v5(coordinator, region)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            self.wfile.write(json.dumps(data, default=str).encode())
            
        except Exception as e:
            print(f"ERROR in v5_intelligence: {str(e)}")
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
