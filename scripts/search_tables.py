
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv("c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/.env.local")

def search_tables():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='bi_assetplan'
    )
    cursor = conn.cursor()
    
    print("--- Searching for Reservas tables ---")
    cursor.execute("SHOW TABLES LIKE '%Reserva%'")
    for t in cursor.fetchall(): print(t[0])
    
    print("\n--- Searching for Contratos tables ---")
    cursor.execute("SHOW TABLES LIKE '%Contrato%'")
    for t in cursor.fetchall(): print(t[0])
    
    conn.close()

if __name__ == "__main__":
    search_tables()
