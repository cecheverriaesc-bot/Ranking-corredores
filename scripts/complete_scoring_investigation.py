#!/usr/bin/env python3
"""
Investigation for completing the scoring metrics.
Focus: Visits, cancellations, and response times.
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
print("INVESTIGATING MISSING METRICS")
print("=" * 80)

# 1. Visits metrics from bi_DimAgendas
print("\n--- SAMPLE AGENDAS (Visits) ---")
cursor.execute("""
    SELECT corredor_id, estado, COUNT(*) as count
    FROM bi_DimAgendas
    WHERE corredor_id IS NOT NULL
    GROUP BY corredor_id, estado
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"  Corredor {row['corredor_id']}: {row['estado']} = {row['count']} visitas")

print("\n--- UNIQUE ESTADOS IN AGENDAS ---")
cursor.execute("SELECT DISTINCT estado FROM bi_DimAgendas WHERE estado IS NOT NULL")
estados = [r['estado'] for r in cursor.fetchall()]
print(f"  {', '.join(estados)}")

# 2. Lead response time (lag_contacto)
print("\n--- LEAD LAG_CONTACTO (Response time) ---")
cursor.execute("""
    SELECT 
        corredor_id,
        AVG(lag_contacto) as avg_lag,
        COUNT(*) as total_leads,
        SUM(CASE WHEN lag_contacto <= 24 THEN 1 ELSE 0 END) as contacto_24h
    FROM bi_DimLeads
    WHERE corredor_id IS NOT NULL AND lag_contacto IS NOT NULL
    GROUP BY corredor_id
    LIMIT 5
""")
print("  Corredor | Avg Lag (h) | Total | <24h")
print("  " + "-" * 50)
for row in cursor.fetchall():
    pct_24h = (row['contacto_24h'] / row['total_leads'] * 100) if row['total_leads'] > 0 else 0
    print(f"  {row['corredor_id']:8} | {row['avg_lag']:11.1f} | {row['total_leads']:5} | {pct_24h:5.1f}%")

# 3. Check if we can calculate leads tomados
print("\n--- CHECKING LEADS TOMADOS CALCULATION ---")
cursor.execute("""
    SELECT 
        corredor_id,
        SUM(step_1_epc_tomado) as leads_tomados,
        COUNT(DISTINCT lead_id) as total_leads
    FROM bi_DimLeads
    WHERE corredor_id IS NOT NULL
    GROUP BY corredor_id
    LIMIT 5
""")
print("  Corredor | Leads Tomados | Total Leads")
print("  " + "-" * 50)
for row in cursor.fetchall():
    print(f"  {row['corredor_id']:8} | {row['leads_tomados']:13} | {row['total_leads']:11}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)
