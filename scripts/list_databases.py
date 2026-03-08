import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
        user="carlos.echeverria",
        password="JS5tyLBSMBdAdzAQ9r6UF2g7"
    )

def list_databases():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    dbs = cursor.fetchall()
    print("Databases found:")
    for db in dbs:
        print(f" - {db[0]}")
    conn.close()

if __name__ == "__main__":
    list_databases()
