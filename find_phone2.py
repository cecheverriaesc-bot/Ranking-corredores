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
    try:
        cursor.execute(f"DESCRIBE {t}")
        cols = [col[0] for col in cursor.fetchall()]
        if 'tele' in ' '.join(cols).lower() or 'phone' in ' '.join(cols).lower() or 'celular' in ' '.join(cols).lower():
            print(f"Table {t} has columns: {cols}")
    except Exception as e:
        pass
