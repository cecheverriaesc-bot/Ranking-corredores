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

cursor = conn.cursor(dictionary=True)

print("\n=== SCORING EXISTENTE EN BI ===\n")
cursor.execute("""
    SELECT 
        nombre_corredor,
        score_final,
        score_gestion,
        score_rendimiento,
        score_operativo,
        categoria
    FROM bi_DimCorredores
    WHERE coordinador = 'carlos.echeverria' AND activo = 1
    ORDER BY CAST(score_final AS DECIMAL(10,2)) DESC
    LIMIT 5
""")

print("TOP 5 por Score Final:")
for r in cursor.fetchall():
    print(f"  {r['nombre_corredor']:25} | Final:{r['score_final']:>7} | Gest:{r['score_gestion']:>7} | Rend:{r['score_rendimiento']:>7} | Categ:{r['categoria']}")

print("\n=== ZENDESK TABLES ===\n")
cursor.execute("SHOW TABLES LIKE '%zendesk%'")
tables = [r[0] for r in cursor.fetchall()]
if tables:
    print(f"Found: {', '.join(tables)}")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count']
        print(f"  {table}: {count} rows")
else:
    print("No Zendesk tables found")

cursor.close()
conn.close()
