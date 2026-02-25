
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv("c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/.env.local")

def inspect_schema():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='bi_assetplan'
    )
    cursor = conn.cursor()
    
    print("--- bi_DimContratos ---")
    cursor.execute("DESCRIBE bi_DimContratos")
    for col in cursor.fetchall(): print(col)
    
    print("\n--- bi_DimCorredores ---")
    cursor.execute("DESCRIBE bi_DimCorredores")
    for col in cursor.fetchall(): print(col)
    
    conn.close()

if __name__ == "__main__":
    inspect_schema()
