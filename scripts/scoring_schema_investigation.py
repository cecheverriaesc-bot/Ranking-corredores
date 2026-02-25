#!/usr/bin/env python3
"""
Schema investigation to map exact columns needed for broker scoring.
Focus: Engagement (35%) + Rendimiento (40%) = 75% scoring
"""
import mysql.connector
import os
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

print("=" * 80)
print("SCORING METRICS INVESTIGATION")
print("=" * 80)

# Check bi_DimCorredores structure
print("\n--- bi_DimCorredores (Main broker metrics) ---")
cursor.execute("DESCRIBE bi_DimCorredores")
cols = cursor.fetchall()
for col in cols:
    print(f"  {col[0]:40} | {col[1]}")

# Check bi_DimAgendas for visit metrics
print("\n--- bi_DimAgendas (Visit tracking) ---")
cursor.execute("DESCRIBE bi_DimAgendas")
cols = cursor.fetchall()
for col in cols:
    print(f"  {col[0]:40} | {col[1]}")

# Check bi_DimLeads for lead status
print("\n--- bi_DimLeads (Lead lifecycle) ---")
cursor.execute("DESCRIBE bi_DimLeads")
cols = cursor.fetchall()
for col in cols:
    print(f"  {col[0]:40} | {col[1]}")

# Check bi_DimLeadAttemps for activity tracking
print("\n--- bi_DimLeadAttemps (Lead activity) ---")
cursor.execute("DESCRIBE bi_DimLeadAttemps")
cols = cursor.fetchall()
for col in cols:
    print(f"  {col[0]:40} | {col[1]}")

# Sample data from bi_DimCorredores to understand values
print("\n" + "=" * 80)
print("SAMPLE DATA ANALYSIS")
print("=" * 80)

cursor.execute("""
    SELECT 
        nombre_corredor,
        cant_leads,
        reserva,
        porcentaje_convertido_prospecto,
        porcentaje_convertido_contrato,
        prospectos_sin_gestion,
        agendas_corredor
    FROM bi_DimCorredores
    WHERE coordinador = 'carlos.echeverria' AND activo = 1
    LIMIT 3
""")

print("\n--- Sample broker records ---")
rows = cursor.fetchall()
if rows:
    print(f"{'Broker':25} | {'Leads':5} | {'Reservas':3} | {'Conv%':5} | {'Sin Gest':3} | {'Agendas':3}")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]:25} | {row[1]:5} | {row[2]:3} | {row[3]:5} | {row[5]:3} | {row[6]:3}")

# Check if there are temporal fields
print("\n--- Checking for temporal granularity ---")
cursor.execute("SHOW TABLES LIKE 'bi_Dim%'")
tables = [row[0] for row in cursor.fetchall()]
print(f"Found {len(tables)} dimension tables:")
for table in tables:
    cursor.execute(f"DESCRIBE {table}")
    cols = cursor.fetchall()
    has_date = any('fecha' in col[0].lower() or 'date' in col[0].lower() or 'created' in col[0].lower() 
                   for col in cols)
    if has_date:
        date_cols = [col[0] for col in cols if 'fecha' in col[0].lower() or 'date' in col[0].lower() or 'created' in col[0].lower()]
        print(f"  {table:40} → {', '.join(date_cols)}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)
