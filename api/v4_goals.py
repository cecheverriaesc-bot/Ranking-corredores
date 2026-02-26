#!/usr/bin/env python3
"""
API Endpoint: Broker Goals Management (File-based)
Permite a los corredores establecer y gestionar sus metas personales mensuales.
Guarda los datos en un archivo JSON (no requiere permisos de DB).
"""

from http.server import BaseHTTPRequestHandler
import mysql.connector
import json
import os
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

# Import rate limiter y CORS
import sys
sys.path.append(os.path.dirname(__file__))
from rate_limiter import check_rate_limit, APIRateLimits, send_cors_headers, validate_query_params

# Load environment variables
def load_env_vars():
    env_vars = {}
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

    for key in ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_PORT']:
        if key in os.environ:
            env_vars[key] = os.environ[key]

    return env_vars

ENV_VARS = load_env_vars()

# Path para guardar las metas (en el mismo directorio que este archivo)
GOALS_FILE_PATH = os.path.join(os.path.dirname(__file__), 'broker_goals.json')

def get_bi_connection():
    """Conexión a bi_assetplan para datos históricos"""
    return mysql.connector.connect(
        host=ENV_VARS.get("DB_HOST"),
        user=ENV_VARS.get("DB_USER"),
        password=ENV_VARS.get("DB_PASSWORD"),
        port=int(ENV_VARS.get("DB_PORT", 3306)),
        database="bi_assetplan"
    )


def load_goals_from_file() -> dict:
    """Carga las metas desde el archivo JSON"""
    if os.path.exists(GOALS_FILE_PATH):
        try:
            with open(GOALS_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_goals_to_file(data: dict) -> bool:
    """Guarda las metas en el archivo JSON"""
    try:
        with open(GOALS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving goals file: {e}")
        return False


def calculate_suggested_goal(broker_name: str, target_month: str) -> dict:
    """
    Calcula la meta sugerida para un corredor en un mes específico.
    """
    conn_bi = get_bi_connection()
    cursor = conn_bi.cursor(dictionary=True)
    
    try:
        # 1. Histórico personal (últimos 3 meses)
        cursor.execute("""
            SELECT 
                AVG(reservas) as avg_reservas_3m,
                MAX(reservas) as max_reservas_3m,
                COUNT(*) as months_with_data
            FROM (
                SELECT 
                    DATE_FORMAT(fecha, '%Y-%m-01') as mes,
                    COUNT(*) as reservas
                FROM bi_DimContratos
                WHERE corredor = %s
                  AND fecha >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
                  AND fecha < DATE_FORMAT(%s, '%%Y-%%m-01')
                GROUP BY DATE_FORMAT(fecha, '%%Y-%%m-01')
            ) as monthly_reservas
        """, (broker_name, target_month))
        
        historical = cursor.fetchone()
        avg_3m = float(historical['avg_reservas_3m'] or 0)
        max_3m = int(historical['max_reservas_3m'] or 0)
        
        # 2. Rendimiento año anterior (mismo mes)
        prev_year_month = (datetime.strptime(target_month, '%Y-%m-01') - timedelta(days=365)).strftime('%Y-%m-01')
        cursor.execute("""
            SELECT COUNT(*) as reservas_prev_year
            FROM bi_DimContratos
            WHERE corredor = %s
              AND DATE_FORMAT(fecha, '%%Y-%%m-01') = %s
        """, (broker_name, prev_year_month))
        
        prev_year = cursor.fetchone()
        prev_year_reservas = int(prev_year['reservas_prev_year'] or 0)
        
        # 3. Proyección ritmo actual (mes en curso)
        current_month = datetime.now().strftime('%Y-%m-01')
        cursor.execute("""
            SELECT 
                COUNT(*) as current_reservas,
                DAY(NOW()) as current_day,
                DAY(LAST_DAY(NOW())) as days_in_month
            FROM bi_DimContratos
            WHERE corredor = %s
              AND DATE_FORMAT(fecha, '%%Y-%%m-01') = %s
        """, (broker_name, current_month))
        
        current = cursor.fetchone()
        current_reservas = int(current['current_reservas'] or 0)
        current_day = int(current['current_day'] or 1)
        days_in_month = int(current['days_in_month'] or 30)
        
        # Proyección = reservas_actuales * (dias_totales / dias_transcurridos)
        projection = 0
        if current_day > 0:
            projection = current_reservas * (days_in_month / current_day)
        
        # 4. Cálculo ponderado
        weights = {
            'historical': 0.4,
            'prev_year': 0.2,
            'projection': 0.4
        }
        
        suggested = 0
        if avg_3m > 0:
            suggested += avg_3m * weights['historical']
        if prev_year_reservas > 0:
            suggested += prev_year_reservas * weights['prev_year']
        if projection > 0:
            suggested += projection * weights['projection']
        
        # Si no hay datos históricos, usar proyección o default
        if suggested == 0:
            suggested = max(projection, 10)  # Mínimo 10 reservas
        
        # Redondear al múltiplo de 5 más cercano
        suggested = round(suggested / 5) * 5
        
        # Determinar confianza del cálculo
        confidence = 'low'
        if historical['months_with_data'] >= 3 and prev_year_reservas > 0:
            confidence = 'high'
        elif historical['months_with_data'] >= 2:
            confidence = 'medium'
        
        return {
            'suggested_goal': int(suggested),
            'breakdown': {
                'historical_avg_3m': round(avg_3m, 1),
                'max_last_3m': max_3m,
                'prev_year_same_month': prev_year_reservas,
                'current_projection': round(projection, 1),
                'current_reservas': current_reservas
            },
            'confidence': confidence,
            'calculation_method': 'weighted_average'
        }
        
    except Exception as e:
        print(f"Error calculating suggested goal: {e}")
        return {
            'suggested_goal': 15,  # Default
            'breakdown': {},
            'confidence': 'low',
            'calculation_method': 'default'
        }
    finally:
        cursor.close()
        conn_bi.close()


def get_broker_goal(broker_name: str, goal_month: str) -> dict:
    """Obtiene la meta personal de un corredor para un mes específico"""
    all_goals = load_goals_from_file()
    month_key = goal_month[:7]  # YYYY-MM
    
    if month_key in all_goals:
        return all_goals[month_key].get(broker_name)
    return None


def save_broker_goal(data: dict) -> dict:
    """Guarda o actualiza la meta personal de un corredor"""
    all_goals = load_goals_from_file()
    
    # Extraer mes (YYYY-MM)
    month_key = data['goal_month'][:7]
    
    # Crear estructura si no existe
    if month_key not in all_goals:
        all_goals[month_key] = {}
    
    # Verificar si ya existe para determinar si es update o insert
    existing = all_goals[month_key].get(data['broker_name'])
    
    # Guardar/actualizar
    all_goals[month_key][data['broker_name']] = {
        'broker_name': data['broker_name'],
        'broker_email': data.get('broker_email', ''),
        'goal_month': data['goal_month'],
        'personal_goal': data['personal_goal'],
        'suggested_goal': data.get('suggested_goal', 0),
        'commitment_comment': data.get('commitment_comment', ''),
        'calculation_method': data.get('calculation_method', 'manual'),
        'created_by': 'broker',
        'updated_at': datetime.now().isoformat()
    }
    
    if not existing:
        all_goals[month_key][data['broker_name']]['created_at'] = datetime.now().isoformat()
    
    # Guardar en archivo
    if save_goals_to_file(all_goals):
        return {
            'success': True,
            'message': 'Meta guardada exitosamente',
            'goal_id': data['broker_name'] + '_' + month_key
        }
    else:
        return {
            'success': False,
            'message': 'Error al guardar en archivo'
        }


def get_all_broker_goals(goal_month: str) -> list:
    """Obtiene todas las metas de corredores para un mes específico"""
    all_goals = load_goals_from_file()
    month_key = goal_month[:7]  # YYYY-MM
    
    if month_key in all_goals:
        return list(all_goals[month_key].values())
    return []


# ============================================
# HTTP REQUEST HANDLER
# ============================================

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        GET /api/v4_goals?month=2026-02&broker=Rosangela+Cirelli
        GET /api/v4_goals?month=2026-02 (todas las metas del mes)
        GET /api/v4_goals/suggest?broker=Rosangela+Cirelli&month=2026-02
        """
        # Rate limiting
        if not check_rate_limit(self, APIRateLimits.DATA_API):
            return
        
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # Validar parámetros
        validators = {
            'month': (str, None, None, False),
            'broker': (str, None, None, False)
        }
        validated, error = validate_query_params(query_params, validators)
        
        if error and not parsed_path.path.endswith('/suggest'):
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            send_cors_headers(self, self.headers.get('Origin', ''))
            self.end_headers()
            self.wfile.write(json.dumps({'error': error}).encode())
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        send_cors_headers(self, self.headers.get('Origin', ''))
        self.end_headers()

        try:
            # Endpoint: Calcular meta sugerida
            if parsed_path.path.endswith('/suggest'):
                broker_name = query_params.get('broker', [None])[0]
                month = query_params.get('month', [None])[0]

                if not broker_name or not month:
                    response = {'error': 'broker y month son requeridos'}
                else:
                    response = calculate_suggested_goal(broker_name, month)

                self.wfile.write(json.dumps(response).encode())
                return

            # Endpoint: Obtener metas
            month = query_params.get('month', [None])[0]
            broker = query_params.get('broker', [None])[0]

            if not month:
                # Usar mes actual por defecto
                month = datetime.now().strftime('%Y-%m-01')

            if broker:
                # Meta de un corredor específico
                result = get_broker_goal(broker, month)
                if result:
                    # Calcular meta sugerida actualizada
                    suggested = calculate_suggested_goal(broker, month)
                    result['suggested_goal_calc'] = suggested
                response = result if result else {'message': 'No goal found'}
            else:
                # Todas las metas del mes
                response = get_all_broker_goals(month)

            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_POST(self):
        """
        POST /api/v4_goals
        Body: {
            "broker_name": "Rosangela Cirelli",
            "broker_email": "rosangela@example.com",
            "goal_month": "2026-02-01",
            "personal_goal": 49,
            "commitment_comment": "Mi compromiso es...",
            "calculation_method": "manual"
        }
        """
        # Rate limiting para writes
        if not check_rate_limit(self, APIRateLimits.WRITE_API):
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))

            # Validaciones mínimas
            if not data.get('broker_name') or not data.get('goal_month'):
                response = {
                    'success': False,
                    'message': 'broker_name y goal_month son requeridos'
                }
            else:
                # Normalizar goal_month a primer día del mes
                month_str = data['goal_month']
                if len(month_str) == 7:  # Formato YYYY-MM
                    month_str += '-01'
                data['goal_month'] = month_str

                response = save_broker_goal(data)

        except json.JSONDecodeError:
            response = {'success': False, 'message': 'Invalid JSON'}
        except Exception as e:
            response = {'success': False, 'message': str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        send_cors_headers(self, self.headers.get('Origin', ''))
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        send_cors_headers(self, self.headers.get('Origin', ''))
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
