import mysql.connector
import os
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(
        host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
        user="carlos.echeverria",
        password="JS5tyLBSMBdAdzAQ9r6UF2g7",
        database="bi_assetplan"
    )

def run_audit():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Metas Marzo 2026 (De goals.py)
    goal_contracts = 1499
    goal_reserves = 1656
    
    print(f"--- AUDITORIA MARZO 2026 ---")
    
    # 2. Avance Real (Contratos creados en Marzo)
    cursor.execute("""
        SELECT COUNT(DISTINCT lead_id) as total
        FROM bi_DimLeads
        WHERE YEAR(contrato_created_at) = 2026 AND MONTH(contrato_created_at) = 3
    """)
    real_contracts = cursor.fetchone()['total'] or 0
    
    # 3. Avance Real (Reservas en Marzo)
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM bi_DimReservas
        WHERE YEAR(fecha) = 2026 AND MONTH(fecha) = 3
    """)
    real_reserves = cursor.fetchone()['total'] or 0

    print(f"Contratos: {real_contracts} / {goal_contracts} ({real_contracts/goal_contracts*100:.1f}%)")
    print(f"Reservas: {real_reserves} / {goal_reserves} ({real_reserves/goal_reserves*100:.1f}%)")
    
    # 4. Corredores Activos (Marzo)
    cursor.execute("""
        SELECT COUNT(DISTINCT corredor_id) as total
        FROM bi_DimLeads
        WHERE YEAR(fecha_tomado) = 2026 AND MONTH(fecha_tomado) = 3
    """)
    active_march = cursor.fetchone()['total'] or 0
    print(f"Corredores Activos Marzo: {active_march}")
    
    # 5. Top Performers (Marzo)
    cursor.execute("""
        SELECT c.nombre_corredor, COUNT(DISTINCT l.lead_id) as contratos
        FROM bi_DimLeads l
        JOIN bi_DimCorredores c ON l.corredor_id = c.id
        WHERE YEAR(l.contrato_created_at) = 2026 AND MONTH(l.contrato_created_at) = 3
        GROUP BY c.nombre_corredor
        ORDER BY contratos DESC
        LIMIT 5
    """)
    tops = cursor.fetchall()
    print("Top Performers (Contratos):")
    for t in tops:
        print(f"- {t['nombre_corredor']}: {t['contratos']}")

    conn.close()

if __name__ == "__main__":
    run_audit()
