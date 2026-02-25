#!/usr/bin/env python3
"""
API Endpoint: Ranking Data (Unified)
Obtiene datos del ranking para cualquier mes dinámicamente desde la base de datos.
"""

from http.server import BaseHTTPRequestHandler
import mysql.connector
import json
import os
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

# Load environment variables
def load_env_vars():
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

def get_rentas_connection():
    """Conexión a assetplan_rentas para reservas"""
    return mysql.connector.connect(
        host=ENV_VARS.get("DB_HOST"),
        user=ENV_VARS.get("DB_USER"),
        password=ENV_VARS.get("DB_PASSWORD"),
        port=int(ENV_VARS.get("DB_PORT", 3306)),
        database="assetplan_rentas"
    )

def get_bi_connection():
    """Conexión a bi_assetplan para datos históricos"""
    return mysql.connector.connect(
        host=ENV_VARS.get("DB_HOST"),
        user=ENV_VARS.get("DB_USER"),
        password=ENV_VARS.get("DB_PASSWORD"),
        port=int(ENV_VARS.get("DB_PORT", 3306)),
        database="bi_assetplan"
    )

def get_squad_email(coordinator_email):
    """Mapea email de coordinador a squads oficiales"""
    if not coordinator_email:
        return "carlos.echeverria@assetplan.cl"
    email = coordinator_email.lower().strip()
    squads = [
        "carlos.echeverria@assetplan.cl",
        "luis.gomez@assetplan.cl",
        "nataly.espinoza@assetplan.cl",
        "angely.rojo@assetplan.cl",
        "maria.chacin@assetplan.cl"
    ]
    if email in squads:
        return email
    return "carlos.echeverria@assetplan.cl"

def fetch_ranking_data(year: int, month: int):
    """Obtiene datos del ranking para un mes específico"""
    conn = get_rentas_connection()
    cursor = conn.cursor()
    
    # Calcular fechas del mes
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    
    start_date = f"{year}-{month:02d}-01 00:00:00"
    end_date = f"{next_year}-{next_month:02d}-01 00:00:00"
    
    try:
        # Current Ranking - Solo activos
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
        rows = cursor.fetchall()
        
        # Leads
        cursor.execute("""
            SELECT corredor_id, COUNT(*) 
            FROM leads 
            WHERE created_at BETWEEN %s AND %s 
            GROUP BY corredor_id
        """, (start_date, end_date))
        leads = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Agendas Visitadas
        cursor.execute("""
            SELECT l.corredor_id, COUNT(la.id) 
            FROM lead_agendas la
            JOIN leads l ON la.lead_id = l.id
            WHERE la.visita_fecha BETWEEN %s AND %s AND la.estado = 'Visitado'
            GROUP BY l.corredor_id
        """, (start_date, end_date))
        agendas = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Daily Stats - Solo activos
        cursor.execute("""
            SELECT DATE(r.fecha) as d, u.email as coord, COUNT(r.id) as c
            FROM reservas r 
            JOIN corredores c ON r.corredor_id = c.id
            JOIN users u ON c.coordinador_id = u.id
            LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
            WHERE r.fecha BETWEEN %s AND %s 
              AND c.activo = 1 
              AND (ar.r_caida = 0 OR ar.r_caida IS NULL)
            GROUP BY d, coord
        """, (start_date, end_date))
        daily_raw = cursor.fetchall()
        
        # Procesar ranking
        ranking, others = [], []
        for r in rows:
            name = f"{r[1]} {r[2]}".strip()
            val_gross = int(r[5] or 0)
            val_fallen = int(r[6] or 0)
            net = val_gross - val_fallen
            
            obj = {
                "name": name,
                "val": net,
                "fallen": val_fallen,
                "leads": leads.get(r[0], 0),
                "agendas": agendas.get(r[0], 0),
                "coord": get_squad_email(r[4])
            }
            
            if "reservas adicionales" in name.lower():
                obj["hidden"] = True
            
            if r[3] == 1:  # Externo
                others.append(obj)
            else:
                ranking.append(obj)
        
        ranking.sort(key=lambda x: x['val'], reverse=True)
        others.sort(key=lambda x: x['val'], reverse=True)
        
        # Procesar daily stats
        daily_map = {}
        for d in daily_raw:
            date_str = str(d[0])
            coord_email = get_squad_email(d[1])
            key = (date_str, coord_email)
            daily_map[key] = daily_map.get(key, 0) + int(d[2])
        
        daily_stats = [
            {"date": k[0], "coord": k[1], "count": v} 
            for k, v in sorted(daily_map.items())
        ]
        
        # Last Update (Chile time)
        cursor.execute("SELECT MAX(fecha) FROM reservas WHERE fecha <= NOW()")
        last_res_raw = cursor.fetchone()[0]
        
        last_update_str = "---"
        if last_res_raw:
            chile_time = last_res_raw - timedelta(hours=3)
            last_update_str = chile_time.strftime("%d/%m/%Y %H:%M")
        
        return {
            "ranking": ranking,
            "others": others,
            "daily_stats": daily_stats,
            "last_update": last_update_str
        }
    
    finally:
        cursor.close()
        conn.close()

def fetch_contract_data(year: int, month: int):
    """Obtiene datos de contratos desde BI para un mes específico"""
    conn = get_bi_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Calcular fechas del mes
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{next_year}-{next_month:02d}-01"
    
    try:
        # Contratos por corredor (solo activos)
        cursor.execute("""
            SELECT
                c.nombre_corredor,
                c.corredor_id,
                COUNT(*) as contratos,
                SUM(CASE WHEN c.vigente = 1 THEN 1 ELSE 0 END) as vigentes
            FROM bi_DimContratos c
            WHERE c.created_at BETWEEN %s AND %s
              AND c.corredor_id IS NOT NULL
            GROUP BY c.nombre_corredor, c.corredor_id
            ORDER BY contratos DESC
        """, (start_date, end_date))
        
        contracts_by_broker = {row['nombre_corredor']: row['contratos'] for row in cursor.fetchall()}
        
        # Total contratos del mes
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM bi_DimContratos
            WHERE created_at BETWEEN %s AND %s
        """, (start_date, end_date))
        
        total_contracts = cursor.fetchone()['total']
        
        # Daily contracts
        cursor.execute("""
            SELECT DATE(created_at) as fecha, COUNT(*) as cantidad
            FROM bi_DimContratos
            WHERE created_at BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            ORDER BY fecha
        """, (start_date, end_date))
        
        daily_contracts = [
            {"date": str(row['fecha']), "count": row['cantidad']}
            for row in cursor.fetchall()
        ]
        
        return {
            "contracts_by_broker": contracts_by_broker,
            "total_contracts": total_contracts,
            "daily_contracts": daily_contracts
        }
    
    finally:
        cursor.close()
        conn.close()

def fetch_historical_comparison(year: int, month: int):
    """Obtiene comparación con año anterior"""
    conn = get_rentas_connection()
    cursor = conn.cursor()
    
    prev_year = year - 1
    
    # Calcular fechas del mes
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    
    start_date_prev = f"{prev_year}-{month:02d}-01 00:00:00"
    end_date_prev = f"{prev_year}-{next_month:02d}-01 00:00:00"
    
    try:
        cursor.execute("""
            SELECT COUNT(r.id)
            FROM reservas r
            LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
            WHERE r.fecha BETWEEN %s AND %s
            AND (ar.r_caida = 0 OR ar.r_caida IS NULL)
        """, (start_date_prev, end_date_prev))
        
        result = cursor.fetchone()
        total_prev_year = result[0] if result else 0
        
        return {"total_prev_year": total_prev_year}
    
    finally:
        cursor.close()
        conn.close()

def get_month_goal(year: int, month: int) -> int:
    """Retorna la meta mensual configurada"""
    # Metas configuradas por mes
    GOALS = {
        (2026, 1): 1928,
        (2026, 2): 2174,
    }
    return GOALS.get((year, month), 2000)

def get_contract_goal(year: int, month: int) -> int:
    """Retorna la meta de contratos mensual"""
    CONTRACT_GOALS = {
        (2026, 1): 1928,
        (2026, 2): 2066,
    }
    return CONTRACT_GOALS.get((year, month), 2000)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        GET /api/ranking?year=2026&month=2
        Obtiene datos completos del ranking para un mes específico
        """
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Obtener año y mes de los query params
            year = int(query_params.get('year', [datetime.now().year])[0])
            month = int(query_params.get('month', [datetime.now().month])[0])
            
            # Validar rango
            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12")
            
            # Fetch data
            ranking_data = fetch_ranking_data(year, month)
            contract_data = fetch_contract_data(year, month)
            historical_data = fetch_historical_comparison(year, month)
            
            # Merge contracts into ranking
            for broker in ranking_data['ranking'] + ranking_data['others']:
                broker['contracts'] = contract_data['contracts_by_broker'].get(broker['name'], 0)
            
            # Build response
            response = {
                **ranking_data,
                "total_2025_ytd": historical_data['total_prev_year'],
                "reservation_goal": get_month_goal(year, month),
                "contract_goal": get_contract_goal(year, month),
                "history": {}  # Can be populated if needed
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
