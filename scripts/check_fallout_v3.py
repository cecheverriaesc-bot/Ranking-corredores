
import mysql.connector
import os
import json
from dotenv import load_dotenv

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

def check_fallout():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        months = ['2025-11', '2025-12', '2026-01']
        data = {}
        
        for m in months:
            query = f"""
            SELECT 
                COUNT(r.id) as gross,
                SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as fallen
            FROM reservas r
            LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
            WHERE DATE_FORMAT(r.fecha, '%Y-%m') = '{m}'
            """
            cursor.execute(query)
            row = cursor.fetchone()
            gross = float(row[0] or 0)
            fallen = float(row[1] or 0)
            data[m] = {"gross": gross, "fallen": fallen, "rate": (fallen/gross) if gross else 0}
            
        print(json.dumps(data, indent=2))
        conn.close()
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    check_fallout()
