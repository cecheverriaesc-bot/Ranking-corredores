
import mysql.connector
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load Env
load_dotenv(r"c:\Users\assetplan\Desktop\Ranking Enero 2026\.env")

# DB Connection
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='assetplan_rentas'
    )

# Mapeo de Coordinadores
# We map DB user IDs or Emails to the specific Squad Emails used in frontend
def get_squad_email(coordinator_email):
    # Normalize
    if not coordinator_email: return "carlos.echeverria@assetplan.cl" # Default fallback
    email = coordinator_email.lower().strip()
    
    # Map to Squad Leaders
    squads = [
        "carlos.echeverria@assetplan.cl",
        "luis.gomez@assetplan.cl",
        "nataly.espinoza@assetplan.cl",
        "angely.rojo@assetplan.cl",
        "maria.chacin@assetplan.cl"
    ]
    if email in squads:
        return email
    return "carlos.echeverria@assetplan.cl" # Default

def fetch_ranking_data(conn, start_date, end_date):
    cursor = conn.cursor(dictionary=True)
    
    # Query: ALL Active Corredores (activo=1) LEFT JOIN Reservas
    # This allows counting total squad members even if they have 0 sales.
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

def fetch_history_data(conn, start_date, end_date):
    """
    Fetches data for History (2025).
    CRITICAL: Must include ALL brokers who had reservations, 
    regardless of whether they are currently active or not.
    """
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        c.nombre, 
        c.apellido, 
        COUNT(r.id) as gross_val,
        SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as fallen_val
    FROM reservas r
    JOIN corredores c ON r.corredor_id = c.id
    LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
    WHERE r.fecha BETWEEN %s AND %s
    GROUP BY c.id, c.nombre, c.apellido
    """
    
    cursor.execute(query, (start_date, end_date))
    return cursor.fetchall()

    cursor.execute(query, (start_date, end_date))
    return cursor.fetchall()

def get_last_reservation_date(conn):
    try:
        cursor = conn.cursor()
        query = "SELECT MAX(fecha) FROM reservas WHERE fecha <= NOW()"
        cursor.execute(query)
        res = cursor.fetchone()
        if res and res[0]:
            return res[0] # Returns datetime object
        return None
    except Exception:
        return None


# 2.5 Fetch Leads (Jan 2026)
def fetch_leads_count(conn, start_date, end_date):
    """
    Returns dict: { corredor_id: count }
    """
    cursor = conn.cursor()
    # Assuming 'created_at' is the relevant date for New Leads.
    # Note: If 'Asignados' is the metric, maybe check assigned date?
    # User rule: "Nuevos: Total creados", "Asignados: Con corredor asignado".
    # We want Leads Assigned to that broker. So we group by corredor_id.
    query = """
    SELECT corredor_id, COUNT(*) 
    FROM leads 
    WHERE created_at BETWEEN %s AND %s 
      AND corredor_id IS NOT NULL
    GROUP BY corredor_id
    """
    cursor.execute(query, (start_date, end_date))
    return {row[0]: row[1] for row in cursor.fetchall()}

# 2.6 Fetch Agendas (Jan 2026)
def fetch_agendas_count(conn, start_date, end_date):
    """
    Returns dict: { corredor_id: count }
    Metric: Agendas "Realizadas" (Visitado) linked to broker.
    """
    cursor = conn.cursor()
    # We link via leads table using lead_id.
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

# 2.7 Fetch Daily Stats (Stacked by Coordinator)
def fetch_daily_stats(conn, start_date, end_date):
    """
    Returns list of { date: 'YYYY-MM-DD', coord: 'email', count: N }
    """
    cursor = conn.cursor()
    query = """
    SELECT 
        DATE(r.fecha) as fecha,
        u.email as coordinator_mail,
        COUNT(r.id) as count
    FROM reservas r
    LEFT JOIN corredores c ON r.corredor_id = c.id
    LEFT JOIN users u ON c.coordinador_id = u.id
    WHERE r.fecha BETWEEN %s AND %s
    GROUP BY DATE(r.fecha), u.email
    ORDER BY fecha ASC
    """
    cursor.execute(query, (start_date, end_date))
    rows = cursor.fetchall()
    
    # Process
    results = []
    for r in rows:
        results.append({
            "date": str(r[0]),
            "coord": get_squad_email(r[1]),
            "count": r[2]
        })
    return results

def main():
    try:
        conn = get_connection()
        
        start_date_2026 = '2026-01-01 00:00:00'
        end_date_2026 = '2026-01-31 23:59:59'

        # 1. Fetch CURRENT (Jan 2026)
        print("Fetching Current Data (Jan 2026)...")
        rows_2026 = fetch_ranking_data(conn, start_date_2026, end_date_2026)

        # 1b. Fetch Leads & Agendas
        print("Fetching Leads & Agendas...")
        leads_map = fetch_leads_count(conn, start_date_2026, end_date_2026)
        agendas_map = fetch_agendas_count(conn, start_date_2026, end_date_2026)

        # 1c. Fetch Daily Stats
        print("Fetching Daily Stats...")
        daily_stats = fetch_daily_stats(conn, start_date_2026, end_date_2026)
        
        today = datetime.now()
        # For testing purposes or manual run, we assume 'today' month is Jan.
        # If we are in Feb, this might break, but focus on Jan 2026 ranking.
        
        # 2a. Fetch HISTORY Partial (Jan 1 2025 - Jan X 2025)
        # Calculate same day in 2025.
        # If today is Jan 22 2026, we want Jan 22 2025.
        current_day = today.day
        if today.month != 1: 
             current_day = 31 
             
        end_date_partial_2025 = f'2025-01-{current_day:02d} 23:59:59'
        
        print(f"Fetching History Partial (Jan 1 2025 - Jan {current_day} 2025)...")
        rows_2025_partial = fetch_history_data(conn, '2025-01-01 00:00:00', end_date_partial_2025)

        # 2b. Fetch HISTORY Total (Jan 1 2025 - Jan 31 2025)
        print("Fetching History Total (Jan 2025)...")
        rows_2025_total = fetch_history_data(conn, '2025-01-01 00:00:00', '2025-01-31 23:59:59')
        
        # Helper to process raw rows to dict {name: net_val}
        def process_rows_to_dict(rows):
            d = {}
            for r in rows:
                full_name = f"{r['nombre']} {r['apellido']}".strip()
                net = int(r['gross_val']) - int(r['fallen_val'])
                d[full_name] = net
            return d

        partial_map = process_rows_to_dict(rows_2025_partial)
        total_map = process_rows_to_dict(rows_2025_total)

        history_map = {}
        # Union of names from both maps
        all_hist_names = set(partial_map.keys()) | set(total_map.keys())
        
        for name in all_hist_names:
            c_val = partial_map.get(name, 0)
            t_val = total_map.get(name, 0)
            history_map[name] = { 'c': c_val, 't': t_val } 

        # Process Current Data
        freelance_list = []
        institutional_list = []
        
        # Manual overrides for names if needed (e.g. "Vivao (Nicole Jones)")
        # We will use raw DB name + surname 
        
        names_with_agenda = [] 
        
        today = datetime.now()
        
        for r in rows_2026:
            full_name = f"{r['nombre']} {r['apellido']}".strip()
            # Ensure numbers are int/float not Decimals if connector returns them
            net = int(r['gross_val']) - int(r['fallen_val'])
            fallen = int(r['fallen_val'])
            coord = get_squad_email(r['coordinator_mail'])
            
            # Additional Metrics
            cid = r['id']
            lead_count = leads_map.get(cid, 0)
            agenda_count = agendas_map.get(cid, 0)

            # Construct Obj
            obj = {
                "name": full_name,
                "val": net,
                "fallen": fallen,
                "leads": lead_count,
                "agendas": agenda_count,
                "coord": coord
            }
            
            # Hide "Corredor Reservas Adicionales" but keep in array for totals
            if "reservas adicionales" in full_name.lower():
                obj["hidden"] = True

            if r['externo'] == 1:
                institutional_list.append(obj)
            else:
                freelance_list.append(obj)
                
        # Sort desc by val
        freelance_list.sort(key=lambda x: x['val'], reverse=True)
        institutional_list.sort(key=lambda x: x['val'], reverse=True)
        
        # Generate CONSTANTS.TS content
        # We need to construct the file string manually to preserve variable exports
        
        # 1. Monthly Goal (Static)
        ts_content = "import { CorredorData, HistoryData, TeamConfig } from './types';\n\n"
        ts_content += "export const MONTHLY_GOAL = 1928;\n\n"
        
        # 1.5 Daily Stats
        ts_content += "export interface DailyStat { date: string; coord: string; count: number; }\n"
        ts_content += "export const DAILY_STATS: DailyStat[] = " + json.dumps(daily_stats, indent=4) + ";\n\n"


        
        # 2. Others
        ts_content += "// ============================================================================\n"
        ts_content += "// OTROS CORREDORES (Institucionales / No RM / Switch) - GENERATED DYNAMICALLY\n"
        ts_content += "// ============================================================================\n"
        ts_content += "export const OTHER_BROKERS_2026: CorredorData[] = " + json.dumps(institutional_list, indent=4) + ";\n\n"
        
        # 3. Current Ranking
        ts_content += "// ============================================================================\n"
        ts_content += "// RANKING ENERO 2026 - GENERATED DYNAMICALLY\n"
        ts_content += "// ============================================================================\n"
        ts_content += "export const CURRENT_RANKING_2026: CorredorData[] = " + json.dumps(freelance_list, indent=4) + ";\n\n"
        
        # 4. Names with Agenda (Curated list filtered by active status)
        curated_agenda = [
            "Erika Cepeda", "Henry Rodriguez", "Luis Pernalete", "Mayerling Soto", 
            "Nailet Rojo", "Paul Perdomo", "Rosangela Cirelli", "Sofia Bravo", 
            "Victoria Díaz", "Yanelaine Reyes", "Yessica Asuaje", "Yexica Gomez", 
            "Yinglis Hernandez", "Yonathan Pino"
        ]
        
        # We only keep them if they are in the freelance_list (which only has active=1 brokers)
        # or institutional_list if applicable, but usually they are freelance.
        active_names = {x['name'] for x in freelance_list} | {x['name'] for x in institutional_list}
        final_agenda = [name for name in curated_agenda if name in active_names]
        
        ts_content += "// Curated Agenda Members (Filtered by active status in DB)\n"
        ts_content += "export const NAMES_WITH_AGENDA: string[] = " + json.dumps(final_agenda, indent=4) + ";\n\n"
        
        # 5. History
        ts_content += "// Historical Data Jan 2025\n"
        ts_content += "export const HISTORY_2025: Record<string, HistoryData> = " + json.dumps(history_map, indent=4) + ";\n\n"
        
        # 6. Last Update
        last_date = get_last_reservation_date(conn)
        last_date_str = last_date.strftime("%d/%m/%Y %H:%M") if last_date else datetime.now().strftime("%d/%m/%Y %H:%M")
        ts_content += f"export const LAST_UPDATE = '{last_date_str}';\n\n"

        # 7. Teams (Static constant)
        ts_content += """export const TEAMS: Record<string, TeamConfig> = {
    "carlos.echeverria@assetplan.cl": { name: "Squad Carlos", icon: "Flame", color: "text-orange-600", bg: "bg-orange-50 border-orange-200", my: false },
    "luis.gomez@assetplan.cl": { name: "Squad Luis", icon: "Droplet", color: "text-blue-500", bg: "bg-blue-50 border-blue-200", my: false },
    "nataly.espinoza@assetplan.cl": { name: "Squad Natu", icon: "GraduationCap", color: "text-indigo-600", bg: "bg-indigo-50 border-indigo-200", my: false },
    "angely.rojo@assetplan.cl": { name: "Squad Angely", icon: "Flower2", color: "text-pink-600", bg: "bg-pink-50 border-pink-200", my: false },
    "maria.chacin@assetplan.cl": { name: "Squad Gabriela", icon: "Star", color: "text-yellow-500", bg: "bg-yellow-50 border-yellow-200", my: false }
};
"""

        # Write file
        # Determine path relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to 'ranking-corredores-rm---dashboard' (if script is in scripts/)
        # Actually structure is: dashboard/scripts/etl.py -> dashboard/constants.ts
        output_path = os.path.join(script_dir, "..", "constants.ts")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ts_content)
            
        print(f"Success! Updated constants.ts with {len(freelance_list)} freelancers and {len(institutional_list)} others.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    main()
