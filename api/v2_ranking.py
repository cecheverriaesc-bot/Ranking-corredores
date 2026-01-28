import mysql.connector
import os
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='assetplan_rentas'
    )

def get_squad_email(coordinator_email):
    if not coordinator_email: return "carlos.echeverria@assetplan.cl"
    email = coordinator_email.lower().strip()
    squads = ["carlos.echeverria@assetplan.cl", "luis.gomez@assetplan.cl", "nataly.espinoza@assetplan.cl", "angely.rojo@assetplan.cl", "maria.chacin@assetplan.cl"]
    if email in squads: return email
    return "carlos.echeverria@assetplan.cl"

def fetch_data(conn):
    cursor = conn.cursor()
    start_date = '2026-01-01 00:00:00'
    end_date = '2026-01-31 23:59:59'

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
        val_gross, val_fallen = int(r[5] or 0), int(r[6] or 0)
        net = val_gross - val_fallen
        obj = {"name": name, "val": net, "fallen": val_fallen, "leads": leads.get(r[0], 0), "agendas": agendas.get(r[0], 0), "coord": get_squad_email(r[4])}
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
        # User complained 00:44 (UTC) vs 22:04 (Local).
        # So I will take the UTC time and subtract 3 hours manually.
        from datetime import timedelta
        # If last_res_raw is naive, assume UTC because user sees UTC.
        # Adjust to Chile (UTC-3)
        chile_time = last_res_raw - timedelta(hours=3)
        last_update_str = chile_time.strftime("%d/%m/%Y %H:%M")
    else:
        # Fallback if no reservations
        from datetime import timedelta
        chile_time = datetime.utcnow() - timedelta(hours=3)
        last_update_str = chile_time.strftime("%d/%m/%Y %H:%M")

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
        try:
            conn = get_connection()
            data = fetch_data(conn)
            conn.close()
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
