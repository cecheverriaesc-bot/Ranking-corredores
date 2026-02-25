#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo de participación histórica y metas personalizadas
"""
import mysql.connector, os
from dotenv import load_dotenv

load_dotenv()
conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=int(os.getenv('DB_PORT', 3306)),
    database='bi_assetplan'
)
cursor = conn.cursor(dictionary=True)

# Participación histórica
cursor.execute('SELECT SUM(reserva) as total FROM bi_DimCorredores WHERE activo = 1')
total_global = cursor.fetchone()['total'] or 0

cursor.execute('''
    SELECT SUM(reserva) as total 
    FROM bi_DimCorredores 
    WHERE coordinador = %s AND activo = 1
''', ('carlos.echeverria',))
total_carlos = cursor.fetchone()['total'] or 0

pct = (total_carlos / total_global) if total_global > 0 else 0
meta_carlos = 1707 * pct

print('=' * 60)
print('PARTICIPACION HISTORICA')
print('=' * 60)
print(f'Total Global: {total_global:.0f}')
print(f'Equipo Carlos: {total_carlos:.0f}')
print(f'% Participacion: {pct*100:.2f}%')
print(f'Meta Carlos (110%): {meta_carlos:.0f} contratos/mes')

# Contratos de enero actual
cursor.execute('''
    SELECT COUNT(DISTINCT lead_id) as contratos_enero
    FROM bi_DimLeads
    WHERE contrato_created_at >= %s 
      AND contrato_created_at < %s
      AND corredor_id IN (
          SELECT corredor_id FROM bi_DimCorredores 
          WHERE coordinador = %s AND activo = 1
      )
''', ('2026-01-01', '2026-02-01', 'carlos.echeverria'))
contratos_enero = cursor.fetchone()['contratos_enero'] or 0

print('\n' + '=' * 60)
print('PROGRESO ENERO 2026')
print('=' * 60)
print(f'Contratos actuales: {contratos_enero}')
print(f'Faltante: {meta_carlos - contratos_enero:.0f}')
print(f'Dias restantes: ~2-3 dias')

cursor.close()
conn.close()
