
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv("c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/.env.local")

def test_query():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='bi_assetplan'
    )
    cursor = conn.cursor(dictionary=True)
    
    print("--- Checking Contracts for Feb 2026 ---")
    query = """
    SELECT 
        corredor_id,
        COUNT(*) as contracts_count
    FROM bi_DimContratos
    WHERE created_at BETWEEN '2026-02-01' AND '2026-02-28'
    GROUP BY corredor_id
    LIMIT 10
    """
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
        print(row)
    
    print("\n--- Checking Total Contracts Feb 2026 ---")
    cursor.execute("SELECT COUNT(*) as total FROM bi_DimContratos WHERE created_at BETWEEN '2026-02-01' AND '2026-02-28'")
    print(cursor.fetchone())
    
    conn.close()

if __name__ == "__main__":
    test_query()
