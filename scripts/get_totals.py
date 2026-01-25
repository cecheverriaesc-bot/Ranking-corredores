
import mysql.connector
import os
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
    
    total_gross = 0
    total_fallen = 0
    
    with open(r"c:\Users\assetplan\Desktop\Ranking Enero 2026\totals_output.txt", "w") as f:
        f.write("\n--- RESUMEN ENERO 2026 ---\n")
        f.write(f"{'TIPO':<15} | {'BRUTAS':<8} | {'CAÍDAS':<8} | {'NETO':<8}\n")
        f.write("-" * 55 + "\n")
        
        for r in rows:
            tipo = "Freelance" if r['externo'] == 0 else "Institucional"
            gross = r['gross_val']
            # fix None issue
            fallen = int(r['fallen_val']) if r['fallen_val'] is not None else 0
            net = gross - fallen
            
            total_gross += gross
            total_fallen += fallen
            
            f.write(f"{tipo:<15} | {gross:<8} | {fallen:<8} | {net:<8}\n")
            
        f.write("-" * 55 + "\n")
        net_total = total_gross - total_fallen
        f.write(f"{'TOTAL GLOBAL':<15} | {total_gross:<8} | {total_fallen:<8} | {net_total:<8}\n")

    conn.close()

if __name__ == "__main__":
    main()
