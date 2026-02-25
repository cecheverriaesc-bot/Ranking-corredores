#!/usr/bin/env python3
"""
Deep schema analysis to understand bi_assetplan structure and design proper segmentation.
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
print("PHASE 1: UNDERSTANDING TEMPORAL STRUCTURE")
print("=" * 80)

# Check if bi_DimCorredores has temporal fields
print("\n--- bi_DimCorredores columns ---")
cursor.execute("DESCRIBE bi_DimCorredores")
for col in cursor.fetchall():
    col_name = col[0].lower()
    if any(word in col_name for word in ['fecha', 'date', 'created', 'year', 'month', 'periodo']):
        print(f"  [TEMPORAL] {col[0]} ({col[1]})")
    elif 'region' in col_name or 'comuna' in col_name or 'ubicacion' in col_name:
        print(f"  [GEO] {col[0]} ({col[1]})")

# Check what other dimension tables exist
print("\n--- All dimension/fact tables ---")
cursor.execute("SHOW TABLES LIKE 'bi_%'")
tables = [row[0] for row in cursor.fetchall()]
for table in sorted(tables):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    
    # Check if it has temporal columns
    cursor.execute(f"DESCRIBE {table}")
    cols = cursor.fetchall()
    has_temporal = any('fecha' in col[0].lower() or 'date' in col[0].lower() or 'year' in col[0].lower() 
                      for col in cols)
    has_geo = any('region' in col[0].lower() or 'comuna' in col[0].lower() 
                  for col in cols)
    
    flags = []
    if has_temporal:
        flags.append("TEMPORAL")
    if has_geo:
        flags.append("GEO")
    
    flag_str = f" [{', '.join(flags)}]" if flags else ""
    print(f"  {table:40} | {count:>8} rows{flag_str}")

print("\n" + "=" * 80)
print("PHASE 2: UNDERSTANDING CONTRACT/OP STRUCTURE")
print("=" * 80)

# Look for contract-related tables
print("\n--- Contract/OP related tables ---")
cursor.execute("SHOW TABLES LIKE '%contrato%'")
contrato_tables = [row[0] for row in cursor.fetchall()]
for table in contrato_tables:
    print(f"\n  {table}:")
    cursor.execute(f"DESCRIBE {table} LIMIT 10")
    for col in cursor.fetchall()[:10]:
        print(f"    - {col[0]} ({col[1]})")

# Check if there's a property/OP dimension
cursor.execute("SHOW TABLES LIKE '%property%' OR SHOW TABLES LIKE '%propiedad%'")
prop_tables = [row[0] for row in cursor.fetchall()]
if prop_tables:
    print("\n--- Property tables ---")
    for table in prop_tables:
        print(f"  {table}")

cursor.close()
conn.close()
print("\n" + "=" * 80)
