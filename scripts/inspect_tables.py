#!/usr/bin/env python3
"""
Script para inspeccionar columnas de tablas relevantes y encontrar teléfonos
"""

import os
import mysql.connector
from dotenv import load_dotenv

# Load env
load_dotenv('../../.env')

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='assetplan_rentas'
    )

def get_bi_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database='bi_assetplan'
    )

def inspect_table(conn, table_name):
    """Inspecciona columnas de una tabla"""
    cursor = conn.cursor(dictionary=True)
    
    # Obtener columnas
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
    """, (conn.database, table_name))
    
    columns = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print(f"TABLA: {table_name}")
    print(f"{'='*60}")
    
    if columns:
        print(f"{'Columna':<30} {'Tipo':<15} {'Len':<6} {'Null':<6}")
        print("-" * 60)
        for col in columns:
            len_val = str(col['CHARACTER_MAXIMUM_LENGTH'] or '')[:5]
            null_val = col['IS_NULLABLE']
            print(f"{col['COLUMN_NAME']:<30} {col['DATA_TYPE']:<15} {len_val:<6} {null_val:<6}")
    else:
        print("  No se encontraron columnas o tabla no existe")
    
    cursor.close()
    return [col['COLUMN_NAME'] for col in columns]

def main():
    print("Inspeccionando tablas en assetplan_rentas...")
    conn = get_connection()
    
    # Tablas relevantes
    tables_rentas = ['users', 'corredores', 'leads', 'comments', 'lead_phones']
    
    for table in tables_rentas:
        try:
            inspect_table(conn, table)
        except Exception as e:
            print(f"  Error en {table}: {e}")
    
    conn.close()
    
    print("\n\nInspeccionando tablas en bi_assetplan...")
    bi_conn = get_bi_connection()
    
    tables_bi = ['bi_DimCorredores', 'bi_DimLeads', 'bi_DimAgendas']
    
    for table in tables_bi:
        try:
            inspect_table(bi_conn, table)
        except Exception as e:
            print(f"  Error en {table}: {e}")
    
    bi_conn.close()
    
    print("\n\n=== Búsqueda específica de columnas con 'phone' o 'telefono' ===")
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'assetplan_rentas'
          AND (COLUMN_NAME LIKE '%phone%' OR COLUMN_NAME LIKE '%telefono%' OR COLUMN_NAME LIKE '%movil%' OR COLUMN_NAME LIKE '%celular%')
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """)
    
    phone_columns = cursor.fetchall()
    
    if phone_columns:
        print(f"{'Tabla':<25} {'Columna':<30} {'Tipo'}")
        print("-" * 60)
        for col in phone_columns:
            print(f"{col['TABLE_NAME']:<25} {col['COLUMN_NAME']:<30} {col['DATA_TYPE']}")
    else:
        print("  No se encontraron columnas relacionadas con teléfono")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
