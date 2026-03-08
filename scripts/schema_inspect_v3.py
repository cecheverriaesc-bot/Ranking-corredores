import mysql.connector
import pandas as pd
from datetime import datetime
import os

DB_CONFIG = dict(
    host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
    user="carlos.echeverria",
    password="JS5tyLBSMBdAdzAQ9r6UF2g7",
    port=3306
)

output_lines = []

def p(text=""):
    print(text)
    output_lines.append(str(text))

def bi():
    return mysql.connector.connect(**DB_CONFIG, database="bi_assetplan")

def rentas():
    return mysql.connector.connect(**DB_CONFIG, database="assetplan_rentas")

# 1. Columnas bi_DimReservas
p("=== COLUMNAS bi_DimReservas ===")
conn = bi()
cursor = conn.cursor()
cursor.execute("DESCRIBE bi_DimReservas")
cols_res = cursor.fetchall()
for row in cols_res:
    p(f"  {row[0]:35s} {row[1]}")
conn.close()

# 2. Columnas bi_DimCorredores
p("\n=== COLUMNAS bi_DimCorredores ===")
conn = bi()
cursor = conn.cursor()
cursor.execute("DESCRIBE bi_DimCorredores")
cols_cor = cursor.fetchall()
for row in cols_cor[:40]:
    p(f"  {row[0]:35s} {row[1]}")
conn.close()

# 3. Columnas assetplan_rentas.corredores
p("\n=== COLUMNAS corredores (assetplan_rentas) ===")
try:
    conn = rentas()
    cursor = conn.cursor()
    cursor.execute("DESCRIBE corredores")
    cols_ren = cursor.fetchall()
    for row in cols_ren:
        p(f"  {row[0]:35s} {row[1]}")
    conn.close()
except Exception as e:
    p(f"  Error: {e}")

# Guardar a archivo
out_path = os.path.join(os.path.dirname(__file__), "schema_output.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))
p(f"\nGuardado en: {out_path}")
