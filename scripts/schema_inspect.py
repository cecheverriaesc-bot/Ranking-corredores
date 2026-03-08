import mysql.connector
import pandas as pd
from datetime import datetime, date
import json

DB_CONFIG = dict(
    host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
    user="carlos.echeverria",
    password="JS5tyLBSMBdAdzAQ9r6UF2g7",
    port=3306
)

def bi_conn():
    return mysql.connector.connect(**DB_CONFIG, database="bi_assetplan")

def rentas_conn():
    return mysql.connector.connect(**DB_CONFIG, database="assetplan_rentas")

# ─────────────────────────────────────────────
# 1. INSPECCIONAR ESQUEMA REAL DE TABLAS
# ─────────────────────────────────────────────
print("=" * 60)
print("ESQUEMA bi_DimReservas")
print("=" * 60)
conn = bi_conn()
cur = conn.cursor()
cur.execute("DESCRIBE bi_DimReservas")
cols_res = cur.fetchall()
for c in cols_res:
    print(f"  {c[0]:30s} | {c[1]}")
conn.close()

print("\n" + "=" * 60)
print("ESQUEMA bi_DimCorredores")
print("=" * 60)
conn = bi_conn()
cur = conn.cursor()
cur.execute("DESCRIBE bi_DimCorredores")
cols_cor = cur.fetchall()
for c in cols_cor:
    print(f"  {c[0]:30s} | {c[1]}")
conn.close()

print("\n" + "=" * 60)
print("ESQUEMA reservas (assetplan_rentas)")
print("=" * 60)
try:
    conn = rentas_conn()
    cur = conn.cursor()
    cur.execute("DESCRIBE reservas")
    cols_ren = cur.fetchall()
    for c in cols_ren:
        print(f"  {c[0]:30s} | {c[1]}")
    conn.close()
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
print("SAMPLE bi_DimReservas (5 filas, columnas clave)")
print("=" * 60)
conn = bi_conn()
# Get column names only
col_names = [c[0] for c in cols_res]
# Pick safe columns
safe = col_names[:10]
q = f"SELECT {', '.join(safe)} FROM bi_DimReservas ORDER BY reserva_id DESC LIMIT 5"
df = pd.read_sql(q, conn)
print(df.to_string())
conn.close()
