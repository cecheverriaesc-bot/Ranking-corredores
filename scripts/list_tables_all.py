import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
        user="carlos.echeverria",
        password="JS5tyLBSMBdAdzAQ9r6UF2g7",
        database="bi_assetplan"
    )

def list_all_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Tables in bi_assetplan:")
    for t in tables:
        print(f" - {t[0]}")
    conn.close()

if __name__ == "__main__":
    list_all_tables()
