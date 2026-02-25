
import mysql.connector
import os
from dotenv import load_dotenv

# Load Env like etl_ranking.py
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

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='assetplan_rentas'
    )

def check_fallout():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check last 3 months
    months = ['2025-11', '2025-12', '2026-01']
    
    print("--- Fallout Rate Analysis ---")
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
        gross = row[0] or 0
        fallen = row[1] or 0
        rate = (fallen / gross * 100) if gross > 0 else 0
        
        print(f"Month {m}: Gross={gross}, Fallen={fallen}, Rate={rate:.2f}%")
        
    conn.close()

if __name__ == "__main__":
    check_fallout()
