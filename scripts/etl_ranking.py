
import mysql.connector
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load Env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_options = [
    os.path.join(script_dir, "..", "..", ".env"),
    os.path.join(script_dir, "..", ".env"),
    os.path.join(os.getcwd(), ".env")
]

env_loaded = False
for path in env_options:
    if os.path.exists(path):
        load_dotenv(path)
        print(f"INFO: Cargado .env desde {os.path.abspath(path)}")
        env_loaded = True
        break

if not env_loaded:
    print("WARNING: No se encontro archivo .env en las rutas buscadas.")

# DB Connection
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='assetplan_rentas'
    )

def get_bi_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='bi_assetplan'
    )

# Mapeo de Coordinadores
def get_squad_email(coordinator_email):
    if not coordinator_email: return "sin_asignar@assetplan.cl"
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
    return "sin_asignar@assetplan.cl"

def fetch_last_db_update(conn):
    cursor = conn.cursor()
    query = "SELECT MAX(fecha) FROM reservas"
    cursor.execute(query)
    result = cursor.fetchone()
    if result and result[0]:
        return result[0].strftime('%d/%m/%Y %H:%M')
    return "N/A"





def fetch_ranking_data(conn, start_date, end_date):
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT 
        c.id,
        c.nombre, 
        c.apellido, 
        c.externo,
        u.email as coordinator_mail, 
        COUNT(r.id) as gross_val,
        SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as fallen_val,
        MAX(r.fecha) as last_date
    FROM corredores c
    LEFT JOIN reservas r ON c.id = r.corredor_id AND r.fecha BETWEEN %s AND %s
    LEFT JOIN users u ON c.coordinador_id = u.id
    LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
    WHERE c.activo = 1 AND u.email IS NOT NULL
    GROUP BY c.id, c.nombre, c.apellido, c.externo, u.email
    """
    cursor.execute(query, (start_date, end_date))
    return cursor.fetchall()

def fetch_history_data(conn, start_date, end_date, partial_end=None):
    cursor = conn.cursor(dictionary=True)
    p_end = partial_end if partial_end else end_date
    query = """
    SELECT
        c.nombre,
        c.apellido,
        COUNT(r.id) as gross_val_total,
        SUM(CASE WHEN r.fecha <= %s THEN 1 ELSE 0 END) as gross_val_partial,
        SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as fallen_val
    FROM reservas r
    JOIN corredores c ON r.corredor_id = c.id
    LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
    WHERE r.fecha BETWEEN %s AND %s
      AND c.activo = 1
    GROUP BY c.id, c.nombre, c.apellido
    """
    cursor.execute(query, (p_end, start_date, end_date))
    return cursor.fetchall()

def fetch_leads_count(conn, start_date, end_date):
    cursor = conn.cursor()
    query = """
    SELECT corredor_id, COUNT(*) 
    FROM leads 
    WHERE created_at BETWEEN %s AND %s 
      AND corredor_id IS NOT NULL
    GROUP BY corredor_id
    """
    cursor.execute(query, (start_date, end_date))
    return {row[0]: row[1] for row in cursor.fetchall()}

def fetch_agendas_count(conn, start_date, end_date):
    cursor = conn.cursor()
    query = """
    SELECT l.corredor_id, COUNT(la.id)
    FROM lead_agendas la
    JOIN leads l ON la.lead_id = l.id
    WHERE la.visita_fecha BETWEEN %s AND %s
      AND la.estado = 'Visitado'
      AND l.corredor_id IS NOT NULL
    GROUP BY l.corredor_id
    """
    cursor.execute(query, (start_date, end_date))
    return {row[0]: row[1] for row in cursor.fetchall()}

def fetch_contracts_count(bi_conn, start_date, end_date):
    """Fetch real contract counts per broker from bi_assetplan.
    Query calibrada contra tabla oficial: tipo_renovacion='Nuevo', corredor IS NOT NULL, vigente=1
    """
    cursor = bi_conn.cursor(dictionary=True)
    query = """
    SELECT 
        CAST(corredor_id AS UNSIGNED) as corredor_id,
        COUNT(*) as contracts
    FROM bi_DimContratos
    WHERE created_at BETWEEN %s AND %s
      AND tipo_renovacion = 'Nuevo'
      AND corredor_id IS NOT NULL
      AND vigente = 1
    GROUP BY corredor_id
    """
    cursor.execute(query, (start_date, end_date))
    result = {}
    for row in cursor.fetchall():
        result[int(row['corredor_id'])] = int(row['contracts'])
    return result

def fetch_broker_historical_weights(conn):
    """Calcula el peso de participacion historica de cada corredor activo.
    Usamos datos de los últimos 6 meses para estabilidad.
    """
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT 
        corredor_id,
        COUNT(*) as hist_total
    FROM reservas
    WHERE fecha >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
    GROUP BY corredor_id
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    total_reservas = sum(r['hist_total'] for r in rows) if rows else 1
    return {r['corredor_id']: r['hist_total'] / total_global if (total_global := total_reservas) > 0 else 0 for r in rows}

def fetch_daily_stats(conn, start_date, end_date):
    cursor = conn.cursor()
    query = """
    SELECT 
        DATE(r.fecha) as fecha,
        u.email as coordinator_mail,
        COUNT(r.id) as count
    FROM reservas r
    JOIN corredores c ON r.corredor_id = c.id
    JOIN users u ON c.coordinador_id = u.id
    LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
    WHERE r.fecha BETWEEN %s AND %s
      AND c.activo = 1
      AND u.email IS NOT NULL
      AND (ar.r_caida = 0 OR ar.r_caida IS NULL)
    GROUP BY DATE(r.fecha), u.email
    ORDER BY fecha ASC
    """
    cursor.execute(query, (start_date, end_date))
    rows = cursor.fetchall()
    
    daily_map = {}
    for r in rows:
        date_str = str(r[0])
        norm_coord = get_squad_email(r[1])
        count = r[2]
        key = (date_str, norm_coord)
        daily_map[key] = daily_map.get(key, 0) + count
        
    results = []
    sorted_keys = sorted(daily_map.keys(), key=lambda x: (x[0], x[1]))
    for key in sorted_keys:
        results.append({
            "date": key[0],
            "coord": key[1],
            "count": daily_map[key]
        })
    return results

def fetch_daily_goals_distribution_dynamic(conn, monthly_contract_goal, month_num):
    # SMART GOAL LOGIC V2 (Feb 2026)
    # 1. Safety Margin: 5% (Target = Contracts / 0.95)
    monthly_reservation_target = monthly_contract_goal / 0.95
    
    # 2. Seasonality Weights (Based on 6-month analysis Aug'25-Jan'26)
    # MySQL DAYOFWEEK: 1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri, 7=Sat
    # Weights normalised around 1.0
    weights_map = {
        1: 0.261, # Sunday (Low)
        2: 1.165, # Monday (High)
        3: 1.386, # Tuesday (Peak)
        4: 1.226, # Wednesday
        5: 1.072, # Thursday
        6: 1.149, # Friday
        7: 0.741  # Saturday
    }
    
    if month_num == 1: days_in_month = 31
    elif month_num == 2: days_in_month = 28
    else: days_in_month = 30
    
    # Calculate Total Weight for the specific month structure
    total_month_weight = 0
    daily_weights = {}
    
    for d in range(1, days_in_month + 1):
        # Create date object for 2026 to get correct Day of Week
        dt = datetime(2026, month_num, d)
        # Python weekday: 0=Mon, 6=Sun. 
        # MySQL/Map: 1=Sun, 2=Mon... 
        # Conversion: Python (0) -> Map (2). Python (6) -> Map (1).
        py_wday = dt.weekday()
        if py_wday == 6: mysql_wday = 1
        else: mysql_wday = py_wday + 2
            
        w = weights_map.get(mysql_wday, 1.0)
        daily_weights[d] = w
        total_month_weight += w
        
    # Distribute Target based on weights
    daily_goals = {}
    current_sum = 0
    
    for d in range(1, days_in_month + 1):
        w = daily_weights[d]
        # Formula: (Target * DayWeight) / TotalMonthWeight
        raw_goal = (monthly_reservation_target * w) / total_month_weight
        daily_goals[d] = round(raw_goal, 1)
        current_sum += daily_goals[d]
        
    print(f"INFO: Smart Goal Target={int(monthly_reservation_target)} (Contracts={monthly_contract_goal}), DistSum={int(current_sum)}")
    return daily_goals, int(monthly_reservation_target)

def main():
    conn = None
    bi_conn = None
    try:
        conn = get_connection()
        bi_conn = get_bi_connection()
        last_db_update = fetch_last_db_update(conn)
        hist_weights = fetch_broker_historical_weights(conn)
        
        # Configuration for each month
        MONTHS_CONFIG = [
            {
                "id": "2026-01",
                "goal": 1928,
                "contract_goal": 1928,  # Jan: same as goal
                "start": "2026-01-01 00:00:00",
                "end": "2026-01-31 23:59:59",
                "history_start": "2025-01-01 00:00:00",
                "daily_goal_base_month": 1
            },
            {
                "id": "2026-02",
                "goal": 2066, # 110% of 1878 (stretch target)
                "contract_goal": 2066,  # 110% of 1878 — meta oficial contratos
                "start": "2026-02-01 00:00:00",
                "end": "2026-02-28 23:59:59",
                "history_start": "2025-02-01 00:00:00",
                "daily_goal_base_month": 2
            }
        ]
        
        monthly_data_export = {}
        
        for config in MONTHS_CONFIG:
            mid = config["id"]
            print(f"--- Processing Month: {mid} ---")
            
            start_date = config["start"]
            end_date = config["end"]
            goal = config["goal"]
            
            rows = fetch_ranking_data(conn, start_date, end_date)
            leads_map = fetch_leads_count(conn, start_date, end_date)
            agendas_map = fetch_agendas_count(conn, start_date, end_date)
            contracts_map = fetch_contracts_count(bi_conn, start_date, end_date)
            daily_stats = fetch_daily_stats(conn, start_date, end_date)
            daily_goals, reservation_goal = fetch_daily_goals_distribution_dynamic(conn, goal, config["daily_goal_base_month"])
            
            freelance_list = []
            institutional_list = []
            
            for r in rows:
                full_name = f"{r['nombre']} {r['apellido']}".strip()
                net = int(r['gross_val']) - int(r['fallen_val'])
                fallen = int(r['fallen_val'])
                coord = get_squad_email(r['coordinator_mail'])
                cid = r['id']
                
                # Calcular Meta Personal basada en peso histórico
                weight = hist_weights.get(cid, 0)
                # Si no tiene peso (nuevo), le damos un mínimo proporcional (ej: 0.8 del promedio)
                if weight == 0:
                    active_count = len(rows) if rows else 1
                    weight = 0.8 / active_count
                
                personal_meta = int(config["contract_goal"] * weight)
                if personal_meta < 5: personal_meta = 5 # Meta mínima saludable
                
                obj = {
                    "name": full_name,
                    "val": net,
                    "fallen": fallen,
                    "leads": leads_map.get(cid, 0),
                    "agendas": agendas_map.get(cid, 0),
                    "contracts": contracts_map.get(cid, 0),
                    "personalMeta": personal_meta,
                    "coord": coord
                }
                
                if "reservas adicionales" in full_name.lower():
                    obj["hidden"] = True

                if r['externo'] == 1:
                    institutional_list.append(obj)
                else:
                    freelance_list.append(obj)
            
            freelance_list.sort(key=lambda x: x['val'], reverse=True)
            institutional_list.sort(key=lambda x: x['val'], reverse=True)
            
            # History
            s_2025 = start_date.replace("2026", "2025")
            e_2025_total = end_date.replace("2026", "2025")
            is_current_month = (datetime.now().strftime("%Y-%m") == mid)
            
            if is_current_month:
                now = datetime.now()
                p_end_2025 = f"2025-{now.month:02d}-{now.day:02d} 23:59:59"
            elif mid < datetime.now().strftime("%Y-%m"):
                p_end_2025 = e_2025_total
            else:
                p_end_2025 = s_2025 

            h_rows = fetch_history_data(conn, s_2025, e_2025_total, p_end_2025)
            
            history_map_local = {}
            total_2025 = 0 # This needs to be total of PARTIAL 2025? Or Total Month?
            # Dashboard uses total2025Today for "Vs 2025". This implies PARTIAL.
            
            for r in h_rows:
                full_name = f"{r['nombre']} {r['apellido']}".strip()
                g_partial = int(r['gross_val_partial'] or 0)
                g_total = int(r['gross_val_total'] or 0)
                f_val = int(r['fallen_val'] or 0)
                
                history_map_local[full_name] = {
                    "c": g_partial,
                    "t": g_total - f_val
                }
                total_2025 += g_partial # Sum of partials

            monthly_data_export[mid] = {
                "goal": goal,
                "contract_goal": config["contract_goal"],
                "ranking": freelance_list,
                "others": institutional_list,
                "daily_stats": daily_stats,
                "daily_goals": daily_goals,
                "reservation_goal": reservation_goal,
                "total_2025_ytd": total_2025,
                "history": history_map_local
            }

        # Global History Map Fallback (Curren Month)
        current_month_id = datetime.now().strftime("%Y-%m")
        if current_month_id not in monthly_data_export:
             current_month_id = "2026-02" 
        
        curr_d = monthly_data_export[current_month_id]
        processed_hist = curr_d["history"]

        # Generate TS content
        ts_content = "import { CorredorData, HistoryData, TeamConfig, MonthData } from './types';\n\n"
        ts_content += "export const MONTHLY_DATA: Record<string, MonthData> = " + json.dumps(monthly_data_export, indent=4) + ";\n\n"
        
        # Legacy Exports
        ts_content += f"export const MONTHLY_GOAL = {curr_d['goal']};\n"
        ts_content += f"export const MONTHLY_RESERVATION_GOAL = {curr_d['reservation_goal']};\n"
        ts_content += f"export const CURRENT_RANKING_2026 = MONTHLY_DATA['{current_month_id}'].ranking;\n"
        ts_content += f"export const OTHER_BROKERS_2026 = MONTHLY_DATA['{current_month_id}'].others;\n"
        ts_content += f"export const DAILY_STATS = MONTHLY_DATA['{current_month_id}'].daily_stats;\n"
        ts_content += f"export const DAILY_GOALS = MONTHLY_DATA['{current_month_id}'].daily_goals;\n\n"

        active_names = {x['name'] for x in curr_d['ranking']}
        curated_agenda = [
            "Erika Cepeda", "Henry Rodriguez", "Luis Pernalete", "Mayerling Soto", 
            "Nailet Rojo", "Paul Perdomo", "Rosangela Cirelli", "Sofia Bravo", 
            "Victoria Díaz", "Yanelaine Reyes", "Yessica Asuaje", "Yexica Gomez", 
            "Yinglis Hernandez", "Yonathan Pino"
        ]
        final_agenda = [name for name in curated_agenda if name in active_names]
        ts_content += "export const NAMES_WITH_AGENDA: string[] = " + json.dumps(final_agenda, indent=4) + ";\n\n"
        
        ts_content += "export const HISTORY_2025: Record<string, HistoryData> = " + json.dumps(processed_hist, indent=4) + ";\n"
        ts_content += f"export const LAST_UPDATE = '{datetime.now().strftime('%d/%m/%Y %H:%M')} (Script)';\n"
        ts_content += f"export const LAST_DB_UPDATE = '{last_db_update}';\n\n"
        
        ts_content += """export const TEAMS: Record<string, TeamConfig> = {
    "carlos.echeverria@assetplan.cl": { name: "Carlos Echeverria", icon: "Flame", color: "text-orange-600", bg: "bg-orange-50 border-orange-200", my: false },
    "luis.gomez@assetplan.cl": { name: "Squad Luis", icon: "Droplet", color: "text-blue-500", bg: "bg-blue-50 border-blue-200", my: false },
    "nataly.espinoza@assetplan.cl": { name: "Squad Natu", icon: "GraduationCap", color: "text-indigo-600", bg: "bg-indigo-50 border-indigo-200", my: false },
    "angely.rojo@assetplan.cl": { name: "Squad Angely", icon: "Flower2", color: "text-pink-600", bg: "bg-pink-50 border-pink-200", my: false },
    "maria.chacin@assetplan.cl": { name: "Squad Gabriela", icon: "Star", color: "text-yellow-500", bg: "bg-yellow-50 border-yellow-200", my: false },
    "sin_asignar@assetplan.cl": { name: "Sin Asignar", icon: "UserMinus", color: "text-slate-500", bg: "bg-slate-200 border-slate-300", my: false }
};
"""

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "..", "constants.ts")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ts_content)
            
        print("Success! Updated constants.ts with Multi-Month Data.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
        if bi_conn and bi_conn.is_connected():
            bi_conn.close()

if __name__ == "__main__":
    main()
