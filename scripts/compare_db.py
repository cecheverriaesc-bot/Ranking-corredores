
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv("c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/.env.local")

def compare_data():
    creds = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT", 3306)
    }
    
    # 1. Check raw reservations (assetplan_rentas)
    conn_raw = mysql.connector.connect(**creds, database='assetplan_rentas')
    cursor_raw = conn_raw.cursor()
    cursor_raw.execute("SELECT COUNT(*) FROM reservas WHERE fecha BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'")
    raw_res = cursor_raw.fetchone()[0]
    conn_raw.close()
    
    # 2. Check processed contracts (bi_assetplan)
    conn_bi = mysql.connector.connect(**creds, database='bi_assetplan')
    cursor_bi = conn_bi.cursor()
    cursor_bi.execute("SELECT COUNT(*) FROM bi_DimContratos WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'")
    bi_contracts = cursor_bi.fetchone()[0]
    
    # 3. Check processed reservations (bi_assetplan)
    # The skill mentions bi_DimCorredores has a 'reserva' column, but let's check if there's a bi_DimReservas or similar
    cursor_bi.execute("SHOW TABLES LIKE 'bi_Dim%'")
    tables = cursor_bi.fetchall()
    
    print(f"Raw Reservations (assetplan_rentas.reservas): {raw_res}")
    print(f"BI Contracts (bi_assetplan.bi_DimContratos): {bi_contracts}")
    print(f"BI Tables: {tables}")
    
    conn_bi.close()

if __name__ == "__main__":
    compare_data()
