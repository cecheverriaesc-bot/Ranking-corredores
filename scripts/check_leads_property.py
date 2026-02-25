#!/usr/bin/env python3
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=int(os.getenv('DB_PORT', 3306)),
    database='assetplan_rentas'
)

cursor = conn.cursor()

print("=== COLUMNS IN LEADS TABLE RELATED TO PROPERTY ===")
cursor.execute("DESCRIBE leads")
for col in cursor.fetchall():
    col_name = col[0].lower()
    if 'property' in col_name or 'group' in col_name or 'proyecto' in col_name:
        print(f"  {col[0]} ({col[1]})")

cursor.close()
conn.close()
