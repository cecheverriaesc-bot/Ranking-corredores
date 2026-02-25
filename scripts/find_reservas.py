
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv("c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/.env.local")

def find_reservas_source():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='bi_assetplan'
    )
    cursor = conn.cursor()
    
    # Let's search for any table that has 'reserva' in the name and a date-like column
    cursor.execute("SHOW TABLES LIKE '%reserva%'")
    tables = [t[0] for t in cursor.fetchall()]
    
    for table in tables:
        print(f"--- Table: {table} ---")
        cursor.execute(f"DESCRIBE {table}")
        cols = cursor.fetchall()
        for col in cols:
            if 'date' in col[1].lower() or 'time' in col[1].lower() or 'fecha' in col[0].lower() or 'created' in col[0].lower():
                print(f"  POTENTIAL DATE COL: {col}")
    
    conn.close()

if __name__ == "__main__":
    find_reservas_source()
