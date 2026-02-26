#!/usr/bin/env python3
"""
API Endpoint: Load Capacity Intelligence
Muestra capacidad disponible de corredores para asignación inteligente.
Previene saturación al mostrar límites mensuales, diarios y de gestión.
"""

from http.server import BaseHTTPRequestHandler
import mysql.connector
import json
import os
from datetime import datetime

# Load environment variables - prioritize system env (Vercel) over file
def load_env_vars():
    env_vars = {}
    
    # First, try to load from .env file (for local development)
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
    
    # Override with system environment variables (Vercel uses these)
    for key in ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_PORT']:
        if key in os.environ:
            env_vars[key] = os.environ[key]
    
    return env_vars

ENV_VARS = load_env_vars()

def get_assetplan_rentas_connection():
    """Conexión a assetplan_rentas (base principal, no BI)"""
    return mysql.connector.connect(
        host=ENV_VARS.get("DB_HOST"),
        user=ENV_VARS.get("DB_USER"),
        password=ENV_VARS.get("DB_PASSWORD"),
        port=int(ENV_VARS.get("DB_PORT", 3306)),
        database="assetplan_rentas"  # Base principal
    )

def fetch_broker_capacity(coordinador_email='carlos.echeverria@assetplan.cl'):
    """
    Obtiene capacidad disponible de corredores desde assetplan_rentas.
    Usa la query compartida por el usuario para detectar saturación.
    """
    conn = get_assetplan_rentas_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Query adaptada del código compartido
        cursor.execute("""
            WITH toma_mensual AS (
                SELECT
                    corredores.id AS corredor_id,
                    COUNT(DISTINCT comments.id) AS cantidad_leads_tomados_mes
                FROM comments
                INNER JOIN users ON comments.user_id = users.id
                INNER JOIN corredores ON users.id = corredores.user_id
                WHERE comments.milestone_id = 1
                  AND comments.created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
                  AND corredores.gestiona_leads IS NULL
                GROUP BY corredores.id
            ),
            toma_diaria AS (
                SELECT
                    corredores.id AS corredor_id,
                    COUNT(DISTINCT comments.id) AS cantidad_leads_tomados_dia
                FROM comments
                INNER JOIN users ON comments.user_id = users.id
                INNER JOIN corredores ON users.id = corredores.user_id
                WHERE comments.milestone_id = 1
                  AND comments.created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)
                  AND corredores.gestiona_leads IS NULL
                GROUP BY corredores.id
            ),
            en_gestion AS (
                SELECT
                    corredores.id AS corredor_id,
                    COUNT(DISTINCT l.id) AS leads_activos
                FROM leads l
                INNER JOIN corredores ON l.corredor_id = corredores.id
                WHERE l.estado IN ('ingresado','contactado','pendiente','prospecto','creado','calificado')
                  AND UNIX_TIMESTAMP(l.convertido_prospecto) IS NULL
                  AND UNIX_TIMESTAMP(l.snoozed_at) IS NULL
                GROUP BY corredores.id
            )
            SELECT
                c.id as corredor_id,
                CONCAT(c.nombre," ",c.apellido) AS corredor,
                COALESCE(toma_mensual.cantidad_leads_tomados_mes, 0) as tomados_mes,
                c.limit_to_take_leads AS limite_mensual,
                ROUND(COALESCE(toma_mensual.cantidad_leads_tomados_mes, 0) / NULLIF(c.limit_to_take_leads, 0) * 100, 1) AS uso_mensual_pct,
                COALESCE(toma_diaria.cantidad_leads_tomados_dia, 0) as tomados_dia,
                c.limit_to_take_leads_daily AS limite_diario,
                ROUND(COALESCE(toma_diaria.cantidad_leads_tomados_dia, 0) / NULLIF(c.limit_to_take_leads_daily, 0) * 100, 1) AS uso_diario_pct,
                COALESCE(en_gestion.leads_activos, 0) as en_gestion,
                c.limit_to_manage_leads AS limite_gestion,
                ROUND(COALESCE(en_gestion.leads_activos, 0) / NULLIF(c.limit_to_manage_leads, 0) * 100, 1) AS uso_gestion_pct,
                (CASE 
                    WHEN toma_mensual.cantidad_leads_tomados_mes/NULLIF(c.limit_to_take_leads, 0) >= 1 
                      OR toma_diaria.cantidad_leads_tomados_dia/NULLIF(c.limit_to_take_leads_daily, 0) >= 1 
                      OR en_gestion.leads_activos/NULLIF(c.limit_to_manage_leads, 0) >= 1 
                    THEN 1
                    ELSE 0
                END) AS limitado,
                c.allow_meli_leads,
                (CASE
                    WHEN c.allow_meli_leads = 2 THEN 'permite'
                    WHEN c.allow_meli_leads = 0 THEN 'no_permite'
                    ELSE 'limitado'
                END) AS permite_meli,
                (CASE
                    WHEN c.tipo_corredor = 1 THEN 'Freelance'
                    WHEN c.tipo_corredor IN (2, 3) THEN 'Planta'
                    WHEN c.tipo_corredor IN (4, 5) THEN 'Externo'
                    ELSE 'Staff'
                END) AS tipo_base,
                0 AS is_region  -- TODO: Fix regional detection - leads table doesn't have direct property_group_id
            FROM corredores c
            LEFT JOIN toma_mensual ON c.id = toma_mensual.corredor_id
            LEFT JOIN toma_diaria ON c.id = toma_diaria.corredor_id
            LEFT JOIN en_gestion ON c.id = en_gestion.corredor_id
            WHERE c.activo = 1 
              AND c.gestiona_leads IS NULL
              AND c.coordinador_id IS NOT NULL
            ORDER BY uso_gestion_pct DESC
        """)
        
        brokers = cursor.fetchall()
        
        # Calcular semáforo de capacidad Y recomendaciones de ajuste
        for broker in brokers:
            uso_max = max(
                broker['uso_mensual_pct'] or 0,
                broker['uso_diario_pct'] or 0,
                broker['uso_gestion_pct'] or 0
            )
            
            if broker['limitado'] == 1 or uso_max >= 90:
                broker['capacity_status'] = 'critical'  # 🔴
                broker['capacity_label'] = 'Saturado'
            elif uso_max >= 70:
                broker['capacity_status'] = 'warning'  # 🟡
                broker['capacity_label'] = 'Cuidado'
            else:
                broker['capacity_status'] = 'available'  # 🟢
                broker['capacity_label'] = 'Disponible'
            
            broker['capacity_pct'] = uso_max
            
            # 🧠 NUEVA LÓGICA: Recomendación de ajuste de límites
            # Obtener conversión histórica desde bi_assetplan (asumimos que existe)
            # Por ahora usamos lógica basada solo en capacidad
            # TODO: Cruzar con conversión real de bi_DimCorredores
            
            limite_actual_gestion = broker['limite_gestion'] or 50  # default si es NULL
            leads_en_gestion = broker['en_gestion'] or 0
            
            # Recomendación basada en saturación y rendimiento
            if broker['limitado'] == 1:
                # Saturado: recomendar aumento si está trabajando todo
                margen_actual = limite_actual_gestion - leads_en_gestion
                if margen_actual <= 5:
                    # Está usando casi todo → buena señal, puede manejar más
                    aumento_sugerido = max(10, int(limite_actual_gestion * 0.2))  # +20%
                    broker['limit_recommendation'] = {
                        'action': 'increase',
                        'current': limite_actual_gestion,
                        'suggested': limite_actual_gestion + aumento_sugerido,
                        'increase': aumento_sugerido,
                        'reason': f'Saturado pero eficiente ({leads_en_gestion}/{limite_actual_gestion}). Puede manejar +{aumento_sugerido} leads.'
                    }
                else:
                    # Saturado pero con margen → revisar por qué no toma más
                    broker['limit_recommendation'] = {
                        'action': 'review',
                        'current': limite_actual_gestion,
                        'suggested': limite_actual_gestion,
                        'increase': 0,
                        'reason': f'Saturado con margen de {margen_actual} leads. Revisar por qué no toma más antes de aumentar.'
                    }
            
            elif uso_max >= 80:
                # Cerca del límite: recomendar aumento preventivo
                aumento_sugerido = max(5, int(limite_actual_gestion * 0.15))  # +15%
                broker['limit_recommendation'] = {
                    'action': 'increase',
                    'current': limite_actual_gestion,
                    'suggested': limite_actual_gestion + aumento_sugerido,
                    'increase': aumento_sugerido,
                    'reason': f'Al {int(uso_max)}% de capacidad. Aumentar preventivamente +{aumento_sugerido} para evitar saturación.'
                }
            
            elif uso_max < 50:
                # Bajo uso: no aumentar, posiblemente necesita coaching
                broker['limit_recommendation'] = {
                    'action': 'maintain',
                    'current': limite_actual_gestion,
                    'suggested': limite_actual_gestion,
                    'increase': 0,
                    'reason': f'Solo al {int(uso_max)}% de capacidad. No requiere aumento, puede tomar más con límite actual.'
                }
            
            else:
                # Uso normal (50-79%): mantener y monitorear
                broker['limit_recommendation'] = {
                    'action': 'maintain',
                    'current': limite_actual_gestion,
                    'suggested': limite_actual_gestion,
                    'increase': 0,
                    'reason': f'Uso saludable al {int(uso_max)}%. Límite actual es adecuado.'
                }
        
        return {
            "brokers": brokers,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error fetching capacity: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET request for capacity data"""
        try:
            data = fetch_broker_capacity()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(data, default=str).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
