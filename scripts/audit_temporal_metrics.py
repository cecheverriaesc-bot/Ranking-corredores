#!/usr/bin/env python3
"""
Audit temporal de todas las métricas del Laboratorio
"""
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

cursor = conn.cursor(dictionary=True)

print("=" * 80)
print("AUDITORÍA TEMPORAL DE MÉTRICAS")
print("=" * 80)

# 1. Verificar si bi_DimCorredores tiene fechas
print("\n--- COLUMNAS DE FECHA EN bi_DimCorredores ---")
cursor.execute("DESCRIBE bi_DimCorredores")
date_cols = [col['Field'] for col in cursor.fetchall() if 'fecha' in col['Field'].lower() or 'date' in col['Field'].lower() or 'created' in col['Field'].lower()]
print(f"  Columnas de fecha encontradas: {date_cols if date_cols else 'NINGUNA'}")

# 2. Verificar fecha en bi_DimAgendas
print("\n--- COLUMNAS DE FECHA EN bi_DimAgendas ---")
cursor.execute("DESCRIBE bi_DimAgendas")
agenda_dates = [col['Field'] for col in cursor.fetchall() if 'fecha' in col['Field'].lower() or 'date' in col['Field'].lower() or 'created' in col['Field'].lower()]
print(f"  Columnas: {agenda_dates}")

# 3. Verificar fecha en bi_DimLeads
print("\n--- COLUMNAS DE FECHA EN bi_DimLeads ---")
cursor.execute("DESCRIBE bi_DimLeads")
lead_dates = [col['Field'] for col in cursor.fetchall() if 'fecha' in col['Field'].lower() or 'date' in col['Field'].lower() or 'created' in col['Field'].lower()]
print(f"  Columnas: {lead_dates}")

# 4. Sample de datos con fechas
print("\n--- SAMPLE DE FECHAS EN AGENDAS ---")
cursor.execute(f"""
    SELECT MIN({agenda_dates[0]}) as min_date, MAX({agenda_dates[0]}) as max_date, COUNT(*) as total
    FROM bi_DimAgendas
""" if agenda_dates else "SELECT 'No date columns' as info")
print(f"  {cursor.fetchone()}")

print("\n--- SAMPLE DE FECHAS EN LEADS ---")
cursor.execute(f"""
    SELECT MIN({lead_dates[0]}) as min_date, MAX({lead_dates[0]}) as max_date, COUNT(*) as total
    FROM bi_DimLeads
""" if lead_dates else "SELECT 'No date columns' as info")
print(f"  {cursor.fetchone()}")

# 5. Verificar si hay data de enero 2026
print("\n--- DATA DE ENERO 2026 ---")
if agenda_dates:
    cursor.execute(f"""
        SELECT COUNT(*) as count_enero_2026
        FROM bi_DimAgendas
        WHERE {agenda_dates[0]} >= '2026-01-01' AND {agenda_dates[0]} < '2026-02-01'
    """)
    print(f"  Agendas en Enero 2026: {cursor.fetchone()['count_enero_2026']}")

if lead_dates:
    cursor.execute(f"""
        SELECT COUNT(*) as count_enero_2026
        FROM bi_DimLeads
        WHERE {lead_dates[0]} >= '2026-01-01' AND {lead_dates[0]} < '2026-02-01'
    """)
    print(f"  Leads en Enero 2026: {cursor.fetchone()['count_enero_2026']}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("AUDITORÍA COMPLETADA")
print("=" * 80)
