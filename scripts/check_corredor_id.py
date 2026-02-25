#!/usr/bin/env python3
import mysql.connector, os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=int(os.getenv('DB_PORT', 3306)),
    database='bi_assetplan'
)

cursor = conn.cursor()

print("=== bi_DimCorredores Structure ===")
cursor.execute("DESCRIBE bi_DimCorredores")
for col in cursor.fetchall():
    if 'id' in col[0].lower() or 'corredor' in col[0].lower():
        print(f"  {col[0]:40} | {col[1]}")

cursor.close()
conn.close()
