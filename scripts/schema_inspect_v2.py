import mysql.connector
import pandas as pd
from datetime import datetime
import json
import os

DB_CONFIG = dict(
    host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
    user="carlos.echeverria",
    password="JS5tyLBSMBdAdzAQ9r6UF2g7",
    port=3306
)

def bi():
    return mysql.connector.connect(**DB_CONFIG, database="bi_assetplan")

def rentas():
    return mysql.connector.connect(**DB_CONFIG, database="assetplan_rentas")

# 1. Columnas exactas de bi_DimReservas
print("=== COLUMNAS bi_DimReservas ===")
conn = bi()
cursor = conn.cursor()
cursor.execute("DESCRIBE bi_DimReservas")
for row in cursor.fetchall():
    print(f"  {row[0]:35s} {row[1]}")
conn.close()

# 2. Columnas exactas de bi_DimCorredores
print("\n=== COLUMNAS bi_DimCorredores (primeras 30) ===")
conn = bi()
cursor = conn.cursor()
cursor.execute("DESCRIBE bi_DimCorredores")
rows = cursor.fetchall()
for i, row in enumerate(rows[:30]):
    print(f"  {row[0]:35s} {row[1]}")
conn.close()

# 3. Sample de corredores en rentas 
print("\n=== COLUMNAS corredores (assetplan_rentas) ===")
try:
    conn = rentas()
    cursor = conn.cursor()
    cursor.execute("DESCRIBE corredores")
    for row in cursor.fetchall():
        print(f"  {row[0]:35s} {row[1]}")
    conn.close()
except Exception as e:
    print(f"  Error: {e}")
