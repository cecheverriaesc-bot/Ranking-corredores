
import mysql.connector
import os
import json
from dotenv import load_dotenv

load_dotenv(r"c:\Users\assetplan\Desktop\Ranking Enero 2026\.env")

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='assetplan_rentas'
    )

def main():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        c.externo,
        COUNT(r.id) as gross_val,
        SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as fallen_val
    FROM reservas r
    JOIN corredores c ON r.corredor_id = c.id
    LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
    WHERE r.fecha BETWEEN '2026-01-01 00:00:00' AND '2026-01-31 23:59:59'
    GROUP BY c.externo
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    results = {
        "freelance": {"gross": 0, "fallen": 0, "net": 0},
        "institutional": {"gross": 0, "fallen": 0, "net": 0},
        "global": {"gross": 0, "fallen": 0, "net": 0}
    }
    
    for r in rows:
        gross = r['gross_val']
        fallen = int(r['fallen_val']) if r['fallen_val'] is not None else 0
        net = gross - fallen
        
        target = "institutional" if r['externo'] == 1 else "freelance"
        
        results[target]["gross"] += gross
        results[target]["fallen"] += fallen
        results[target]["net"] += net
        
        results["global"]["gross"] += gross
        results["global"]["fallen"] += fallen
        results["global"]["net"] += net

    with open(r"c:\Users\assetplan\Desktop\Ranking Enero 2026\totals.json", "w") as f:
        json.dump(results, f, indent=4)

    conn.close()

if __name__ == "__main__":
    main()
