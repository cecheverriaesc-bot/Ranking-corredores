import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
        user="carlos.echeverria",
        password="JS5tyLBSMBdAdzAQ9r6UF2g7",
        database="bi_assetplan"
    )

def find_column_in_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Obtener todas las tablas
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    
    print(f"Searching for 'meta_personal' or 'meta' in {len(tables)} tables...")
    
    found_tables = []
    for table in tables:
        try:
            cursor.execute(f"DESCRIBE {table}")
            columns = [c[0].lower() for c in cursor.fetchall()]
            if any("meta" in col for col in columns):
                found_tables.append((table, columns))
        except:
            continue
            
    print("\nTables with 'meta' in columns:")
    for table, cols in found_tables:
        print(f" - {table}")
        for c in cols:
            if "meta" in c:
                print(f"   * {c}")
                
    conn.close()

if __name__ == "__main__":
    find_column_in_tables()
