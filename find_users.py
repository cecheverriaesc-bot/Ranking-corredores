import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=3306,
    database='bi_assetplan'
)
cursor = conn.cursor()

cursor.execute("SHOW TABLES")
tables = [col[0] for col in cursor.fetchall()]

for t in tables:
    if 'asesor' in t.lower() or 'usuario' in t.lower() or 'ejecutivo' in t.lower() or 'corredor' in t.lower() or 'asesor' in t.lower():
        try:
            cursor.execute(f"DESCRIBE {t}")
            cols = [col[0] for col in cursor.fetchall()]
            print(f"Table {t} has columns: {cols}")
        except Exception as e:
            pass
