import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
        user="carlos.echeverria",
        password="JS5tyLBSMBdAdzAQ9r6UF2g7",
        database="bi_assetplan"
    )

def check_last_update():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Ver si hay alguna columna de fecha o ver datos recientes
    cursor.execute("SELECT nombre_corredor, score_final FROM bi_DimCorredores WHERE score_final IS NOT NULL LIMIT 5")
    rows = cursor.fetchall()
    print("Datos actuales en bi_DimCorredores:")
    for r in rows:
        print(r)
        
    conn.close()

if __name__ == "__main__":
    check_last_update()
