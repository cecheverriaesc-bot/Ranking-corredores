
import os
import mysql.connector
from dotenv import load_dotenv


load_dotenv('.env')
load_dotenv('../.env')
load_dotenv('../../.env')


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='assetplan_rentas'
    )

def diagnose():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    names = ["Leandro Osorio Loaiza", "Daniela Sulbaran", "Ninoska Dusan Miranda Ortega"]
    
    print("--- Diagnóstico de Corredores ---")

    for full_name in names:
        parts = full_name.split(' ')
        nombre = parts[0]
        
        query = "SELECT * FROM corredores WHERE nombre LIKE %s"
        cursor.execute(query, (f"{nombre}%",))
        results = cursor.fetchall()
        
        for r in results:
            print(f"Name: {r.get('nombre')} {r.get('apellido')}")
            print(f"  ID: {r.get('id')}")
            print(f"  Activo: {r.get('activo')}")
            print(f"  Details: { {k: v for k, v in r.items() if 'at' in k or 'id' in k} }")
            

            # Check for recent activity
            cursor.execute("SELECT MAX(fecha) as last_res FROM reservas WHERE corredor_id = %s", (r['id'],))
            last_res = cursor.fetchone()
            print(f"  Last Reservation: {last_res['last_res'] if last_res else 'None'}")
            
            cursor.execute("SELECT COUNT(*) as count FROM leads WHERE corredor_id = %s AND created_at >= DATE_SUB(NOW(), INTERVAL 2 MONTH)", (r['id'],))
            leads_2m = cursor.fetchone()
            print(f"  Leads (last 2m): {leads_2m['count'] if leads_2m else 0}")
            print("-" * 20)


            
    conn.close()

if __name__ == "__main__":
    diagnose()
