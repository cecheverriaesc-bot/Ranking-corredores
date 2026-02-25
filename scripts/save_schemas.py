
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv("c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/.env.local")

def save_detailed_schema():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='bi_assetplan'
    )
    cursor = conn.cursor()
    
    tables = ['bi_DimCorredores', 'bi_DimContratos', 'bi_DimReservas', 'bi_FactReservas']
    
    output_path = "c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/Gobernanza_Ranking_2026/ranking-corredores-rm---dashboard/bi_schemas.txt"
    with open(output_path, 'w') as f:
        for table in tables:
            f.write(f"=== {table} ===\n")
            try:
                cursor.execute(f"DESCRIBE {table}")
                for col in cursor.fetchall():
                    f.write(f"{col}\n")
            except Exception as e:
                f.write(f"ERROR: {e}\n")
            f.write("\n")
    
    conn.close()

if __name__ == "__main__":
    save_detailed_schema()
