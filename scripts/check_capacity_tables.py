#!/usr/bin/env python3
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=int(os.getenv('DB_PORT', 3306)),
    database='assetplan_rentas'
)

cursor = conn.cursor()

print("=== TABLES RELATED TO CAPACITY QUERY ===\n")

# Check if these tables exist
tables_needed = ['corredores', 'users', 'comments', 'leads', 'coordinadores', 'property_groups', 'comunas']

for table in tables_needed:
    try:
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        result = cursor.fetchone()
        if result:
            print(f"[OK] {table} - EXISTS")
            # Show sample count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   => Rows: {count}")
        else:
            print(f"[MISSING] {table}")
    except Exception as e:
        print(f"[ERROR] {table}: {e}")

# Check corredor structure
print("\n=== COLUMNS IN 'corredores' ===")
try:
    cursor.execute("DESCRIBE corredores")
    for col in cursor.fetchall():
        print(f"  {col[0]} ({col[1]})")
except Exception as e:
    print(f"Error: {e}")

cursor.close()
conn.close()
