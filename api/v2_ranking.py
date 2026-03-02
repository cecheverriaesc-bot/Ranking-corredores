import mysql.connector
import os
import json
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler

# Import servicios centralizados
import sys
sys.path.append(os.path.dirname(__file__))
from services.metrics_service import (
    calculate_net_reservations,
    validate_squad_email,
    get_reservation_goal,
    get_contract_goal,
)
from utils.dates import get_month_boundaries, format_chile_time

def load_env_vars():
    """Carga variables de entorno desde .env o variables del sistema"""
    env_vars = {}
    env_file_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Sobrescribir con variables de entorno del sistema (para Vercel)
    for key in ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_PORT', 'DB_NAME']:
        if key in os.environ:
            env_vars[key] = os.environ[key]
    
    return env_vars

ENV_VARS = load_env_vars()

def get_connection():
    return mysql.connector.connect(
        host=ENV_VARS.get("DB_HOST"),
        user=ENV_VARS.get("DB_USER"),
        password=ENV_VARS.get("DB_PASSWORD"),
        port=int(ENV_VARS.get("DB_PORT", 3306)),
        database='assetplan_rentas'
    )

def get_squad_email(coordinator_email):
    """Wrapper para servicio centralizado"""
    return validate_squad_email(coordinator_email)

def fetch_data(conn, year: int = 2026, month: int = 1):
    """Obtiene datos del ranking para un mes específico"""
    cursor = conn.cursor()
    
    # Usar servicio centralizado para fechas
    start_date, end_date = get_month_boundaries(year, month)

    # Current Ranking
    cursor.execute("""
    SELECT c.id, c.nombre, c.apellido, c.externo, u.email as coord, 
           COUNT(r.id) as gross, SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as fallen
    FROM corredores c
    LEFT JOIN reservas r ON c.id = r.corredor_id AND r.fecha BETWEEN %s AND %s
    LEFT JOIN users u ON c.coordinador_id = u.id
    LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
    WHERE c.activo = 1 AND u.email IS NOT NULL
    GROUP BY c.id, c.nombre, c.apellido, c.externo, u.email
    """, (start_date, end_date))
    rows_2026 = cursor.fetchall()

    # Leads
    cursor.execute("SELECT corredor_id, COUNT(*) FROM leads WHERE created_at BETWEEN %s AND %s GROUP BY corredor_id", (start_date, end_date))
    leads = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Agendas
    cursor.execute("""
    SELECT l.corredor_id, COUNT(la.id) FROM lead_agendas la
    JOIN leads l ON la.lead_id = l.id
    WHERE la.visita_fecha BETWEEN %s AND %s AND la.estado = 'Visitado'
    GROUP BY l.corredor_id
    """, (start_date, end_date))
    agendas = {row[0]: row[1] for row in cursor.fetchall()}

    # Daily Stats
    cursor.execute("""
    SELECT DATE(r.fecha) as d, u.email as coord, COUNT(r.id) as c
    FROM reservas r JOIN corredores c ON r.corredor_id = c.id
    JOIN users u ON c.coordinador_id = u.id
    LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
    WHERE r.fecha BETWEEN %s AND %s AND c.activo = 1 AND (ar.r_caida = 0 OR ar.r_caida IS NULL)
    GROUP BY d, coord
    """, (start_date, end_date))
    daily_raw = cursor.fetchall()
    
    ranking, others = [], []
    for r in rows_2026:
        name = f"{r[1]} {r[2]}".strip()
        # Usar servicio centralizado para cálculo de net reservations
        net = calculate_net_reservations(r[5], r[6])
        fallen = int(r[6] or 0)
        obj = {"name": name, "val": net, "fallen": fallen, "leads": leads.get(r[0], 0), "agendas": agendas.get(r[0], 0), "coord": get_squad_email(r[4])}
        if "reservas adicionales" in name.lower(): obj["hidden"] = True
        if r[3] == 1: others.append(obj)
        else: ranking.append(obj)

    ranking.sort(key=lambda x: x['val'], reverse=True)
    others.sort(key=lambda x: x['val'], reverse=True)

    daily_map = {}
    for d in daily_raw:
        key = (str(d[0]), get_squad_email(d[1]))
        daily_map[key] = daily_map.get(key, 0) + int(d[2])
    
    daily_stats = [{"date": k[0], "coord": k[1], "count": v} for k, v in sorted(daily_map.items())]

    # Get Last Reservation Time
    # Fallback to 'fecha' since created_at implies it might not exist or be named differently, and error confirmed it doesn't exist.
    cursor.execute("SELECT MAX(fecha) FROM reservas WHERE fecha <= NOW()")
    last_res_raw = cursor.fetchone()[0]

    last_update_str = "---"
    if last_res_raw:
        # Usar servicio centralizado para timezone de Chile
        last_update_str = format_chile_time(last_res_raw, "%d/%m/%Y %H:%M")
    else:
        # Fallback if no reservations
        last_update_str = format_chile_time(datetime.utcnow(), "%d/%m/%Y %H:%M")

    # 2025 Comparison (YTD)
    # Compare 2026-01-01...Now vs 2025-01-01... Same Day/Month
    now = datetime.now()
    # Handle leap years if necessary, but simple mapping is fine for Jan
    end_date_2025 = f"2025-{now.month:02d}-{now.day:02d} 23:59:59"
    
    # 2025 Comparison (YTD) - Net Reservations (Not Fallen) for ALL brokers
    # Compare 2026-01-01...Now vs 2025-01-01... Same Day/Month
    now = datetime.now()
    end_date_2025 = f"2025-{now.month:02d}-{now.day:02d} 23:59:59"
    
    # Query: Count reserves in 2025 range where r_caida is 0 or NULL (Net)
    # We do NOT filter by 'corredores.active' because we want historical reality.
    cursor.execute("""
        SELECT COUNT(r.id) 
        FROM reservas r
        LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
        WHERE r.fecha BETWEEN '2025-01-01 00:00:00' AND %s
        AND (ar.r_caida = 0 OR ar.r_caida IS NULL)
    """, (end_date_2025,))
    
    result_2025 = cursor.fetchone()
    total_2025_ytd = result_2025[0] if result_2025 else 0

    return {
        "ranking": ranking,
        "others": others,
        "daily_stats": daily_stats,
        "last_update": last_update_str,
        "total_2025_ytd": total_2025_ytd
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        GET /api/v2_ranking?year=2026&month=1
        Obtiene datos del ranking para un mes específico (legacy v2)
        """
        try:
            # Obtener parámetros opcionales year y month
            from urllib.parse import parse_qs, urlparse
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            year = int(query_params.get('year', [2026])[0])
            month = int(query_params.get('month', [1])[0])
            
            conn = get_connection()
            data = fetch_data(conn, year, month)
            conn.close()
            
            # Agregar metas centralizadas
            data['reservation_goal'] = get_reservation_goal(year, month)
            data['contract_goal'] = get_contract_goal(year, month)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": f"Fetch failed: {str(e)}"}).encode())
