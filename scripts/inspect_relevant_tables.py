import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
        user="carlos.echeverria",
        password="JS5tyLBSMBdAdzAQ9r6UF2g7",
        database="bi_assetplan"
    )

def inspect_tables_and_columns():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Listar tablas para confirmar nombres exactos
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    print("Tables found:")
    for t in tables:
        if "reserva" in t.lower() or "forecast" in t.lower() or "goal" in t.lower():
            print(f" - {t}")
            # 2. Inspect columns
            cursor.execute(f"DESCRIBE {t}")
            cols = cursor.fetchall()
            for col in cols:
                print(f"   * {col[0]} ({col[1]})")
                
    conn.close()

if __name__ == "__main__":
    inspect_tables_and_columns()
