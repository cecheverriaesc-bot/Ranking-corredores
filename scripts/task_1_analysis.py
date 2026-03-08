import mysql.connector
import os
import pandas as pd
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(
        host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
        user="carlos.echeverria",
        password="JS5tyLBSMBdAdzAQ9r6UF2g7",
        database="bi_assetplan"
    )

def run_task_1():
    conn = get_db_connection()
    
    print("--- TAREA 1: ANALISIS CORREDORES MARZO 2026 ---")
    
    # 1. Avance global del equipo en marzo
    # Nota: Usamos bi_DimReservas si existe, o calculamos desde leads
    query_reservas = """
        SELECT corredor, COUNT(*) as reservas
        FROM bi_DimReservas
        WHERE fecha >= '2026-03-01'
        GROUP BY corredor
    """
    df_reservas = pd.read_sql(query_reservas, conn)
    total_reservas = df_reservas['reservas'].sum()
    
    # Metas (De goals.py / auditoria previa: 1656 reservas total equipo)
    meta_total = 1656 
    
    print(f"Total Reservas Marzo: {total_reservas}")
    print(f"Meta Total Equipo: {meta_total}")
    print(f"Porcentaje Avance: {total_reservas/meta_total*100:.1f}%")
    
    # 2. Performance individual
    # No tengo una tabla f.meta_personal exacta en SQL (esta en JSON), 
    # pero puedo usar un promedio o el historico para estimar si no encuentro el JSON.
    # Intentare buscar el JSON de metas de nuevo.
    
    # 3. Comparativa Enero vs Marzo
    query_comparativa = """
        SELECT 
            corredor,
            SUM(CASE WHEN MONTH(fecha) = 1 THEN 1 ELSE 0 END) as reservas_enero,
            SUM(CASE WHEN MONTH(fecha) = 3 THEN 1 ELSE 0 END) as reservas_marzo
        FROM bi_DimReservas
        WHERE YEAR(fecha) = 2026
        GROUP BY corredor
        ORDER BY reservas_marzo DESC
    """
    df_comp = pd.read_sql(query_comparativa, conn)
    print("\n--- Comparativa Enero vs Marzo ---")
    print(df_comp.head(10))
    
    # Casos especificos: Adriana Ollarves, Alexander Pereira, Henmilys Medina
    targets = ['Adriana Ollarves', 'Alexander Pereira', 'Henmilys Medina']
    print("\n--- Seguimiento Casos Criticos ---")
    for t in targets:
        row = df_comp[df_comp['corredor'].str.contains(t, case=False, na=False)]
        if not row.empty:
            print(f"{t}: Enero={row.iloc[0]['reservas_enero']}, Marzo={row.iloc[0]['reservas_marzo']}")
        else:
            print(f"{t}: No encontrado")

    conn.close()

if __name__ == "__main__":
    run_task_1()
