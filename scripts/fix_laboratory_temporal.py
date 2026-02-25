#!/usr/bin/env python3
"""
URGENTE: Recalcular métricas del Laboratorio con data del MES ACTUAL
No histórico acumulado - solo Enero 2026
"""
import mysql.connector, os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=int(os.getenv('DB_PORT', 3306)),
    database='bi_assetplan'
)

cursor = conn.cursor(dictionary=True)

# MES ACTUAL
YEAR = 2026
MONTH = 1  # Enero

print("=" * 80)
print(f"RECALCULANDO MÉTRICAS DEL LABORATORIO - ENERO {YEAR}")
print("=" * 80)

# 1. Reservas por corredor EN ENERO 2026
print("\n--- RESERVAS ENERO 2026 POR CORREDOR ---")
cursor.execute("""
    SELECT 
        corredor_id,
        COUNT(DISTINCT lead_id) as reservas_mes
    FROM bi_DimLeads
    WHERE YEAR(created_at) = %s 
      AND MONTH(created_at) = %s
      AND (step_4_pool_corredores_reservado = 1 OR step_5_pool_corredores_firmado = 1)
    GROUP BY corredor_id
    ORDER BY reservas_mes DESC
    LIMIT 10
""", (YEAR, MONTH))

print("Top 10 corredores:")
for row in cursor.fetchall():
    print(f"  Corredor {row['corredor_id']}: {row['reservas_mes']} reservas")

# 2. Leads tomados en enero
print("\n--- LEADS TOMADOS ENERO 2026 ---")
cursor.execute("""
    SELECT 
        corredor_id,
        COUNT(*) as leads_tomados_mes
    FROM bi_DimLeads
    WHERE YEAR(fecha_tomado) = %s 
      AND MONTH(fecha_tomado) = %s
      AND corredor_id IS NOT NULL
    GROUP BY corredor_id
    ORDER BY leads_tomados_mes DESC
    LIMIT 5
""", (YEAR, MONTH))

for row in cursor.fetchall():
    print(f"  Corredor {row['corredor_id']}: {row['leads_tomados_mes']} leads")

# 3. Conversión del mes (lead a prospecto)
print("\n--- CONVERSIÓN ENERO 2026 ---")
cursor.execute("""
    SELECT 
        corredor_id,
        COUNT(*) as total_leads,
        SUM(CASE WHEN step_3_pool_corredores_prospecto = 1 THEN 1 ELSE 0 END) as prospectos,
        ROUND(SUM(CASE WHEN step_3_pool_corredores_prospecto = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as conv_pct
    FROM bi_DimLeads
    WHERE YEAR(fecha_tomado) = %s 
      AND MONTH(fecha_tomado) = %s
      AND corredor_id IS NOT NULL
    GROUP BY corredor_id
    HAVING total_leads >= 10
    ORDER BY conv_pct DESC
    LIMIT 5
""", (YEAR, MONTH))

print("Top 5 por conversión:")
for row in cursor.fetchall():
    print(f"  Corredor {row['corredor_id']}: {row['conv_pct']}% ({row['prospectos']}/{row['total_leads']})")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("ANÁLISIS COMPLETADO - DATA EXISTE PARA ENERO 2026")
print("=" * 80)
