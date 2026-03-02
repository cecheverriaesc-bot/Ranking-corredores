import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
conn = mysql.connector.connect(
    host=os.getenv('DB_HOST','').strip(),
    user=os.getenv('DB_USER','').strip(),
    password=os.getenv('DB_PASSWORD','').strip(),
    port=int(os.getenv('DB_PORT', 3306)),
    database='assetplan_rentas'
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT DATE(fecha) as dia, COUNT(*) as cantidad FROM reservas WHERE fecha >= '2026-03-01' GROUP BY DATE(fecha) ORDER BY fecha")
rows = cursor.fetchall()
if not rows:
    print('No hay reservas registradas en BD desde el 1 de Marzo.')
else:
    for row in rows:
        print(f"{row['dia']}: {row['cantidad']} reservas")
conn.close()
