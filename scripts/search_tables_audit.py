import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
        user="carlos.echeverria",
        password="JS5tyLBSMBdAdzAQ9r6UF2g7",
        database="bi_assetplan"
    )

def search_relevant_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    keywords = ["forecast", "meta", "goal", "reserva", "contrato", "corredor", "lead"]
    found = []
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    for t in tables:
        t_name = t[0].lower()
        if any(k in t_name for k in keywords):
            found.append(t[0])
            
    print("Relevant tables found in bi_assetplan:")
    for f in found:
        print(f" - {f}")
        
    conn.close()

if __name__ == "__main__":
    search_relevant_tables()
