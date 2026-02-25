
import mysql.connector
import os
import json
from dotenv import load_dotenv
import statistics

# Load Env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_options = [
    os.path.join(script_dir, "..", "..", ".env"),
    os.path.join(script_dir, "..", ".env"),
    os.path.join(os.getcwd(), ".env")
]

for path in env_options:
    if os.path.exists(path):
        load_dotenv(path)
        break

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='assetplan_rentas'
    )

def analyze():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Analyze last 6 months for better trend data
    start_date = '2025-08-01'
    end_date = '2026-01-31'
    
    print(f"--- ANALYZING RESERVATIONS ({start_date} to {end_date}) ---")

    # 1. By Day of Week (1=Sunday, 2=Monday... 7=Saturday in MySQL? No, standard is 0=Mon, 6=Sun in python, but let's check SQL)
    # MySQL DAYOFWEEK: 1=Sunday, 2=Monday, ..., 7=Saturday
    query_dow = f"""
    SELECT 
        DAYOFWEEK(r.fecha) as day_id,
        DAYNAME(r.fecha) as day_name,
        COUNT(r.id) as total_volume,
        SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as fallen
    FROM reservas r
    LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
    WHERE r.fecha BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY day_id, day_name
    ORDER BY day_id
    """
    cursor.execute(query_dow)
    dow_stats = cursor.fetchall()

    # 2. By Day of Month (1-31)
    query_dom = f"""
    SELECT 
        DAY(r.fecha) as day_num,
        COUNT(r.id) as total_volume,
        SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as fallen
    FROM reservas r
    LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
    WHERE r.fecha BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY day_num
    ORDER BY day_num
    """
    cursor.execute(query_dom)
    dom_stats = cursor.fetchall()
    
    conn.close()

    # Process & Print Findings
    total_res = float(sum(d['total_volume'] for d in dow_stats))
    
    with open("analysis_results.txt", "w") as f:
        f.write("--- DOW WEIGHTS ---\n")
        for d in dow_stats:
            vol = float(d['total_volume'])
            weight = vol / (total_res / 7)
            f.write(f"DAY_{d['day_id']}_{d['day_name']}: {weight:.3f}\n")

        f.write("\n--- WEEK DIST ---\n")
        w1 = float(sum(d['total_volume'] for d in dom_stats if 1 <= d['day_num'] <= 7))
        total_dom = float(sum(d['total_volume'] for d in dom_stats))
        f.write(f"WEEK1_PCT: {w1/total_dom:.3f}\n")
    
    print("Analysis written to analysis_results.txt")

if __name__ == "__main__":
    analyze()
