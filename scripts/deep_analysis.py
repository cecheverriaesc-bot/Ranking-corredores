
import mysql.connector
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv("c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/.env.local")

def get_conn(db):
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=db
    )

output_path = "c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/Gobernanza_Ranking_2026/ranking-corredores-rm---dashboard/analysis_results.txt"

with open(output_path, 'w', encoding='utf-8') as f:
    # =============================================
    # PART 1: RAW DATABASE (assetplan_rentas)
    # =============================================
    f.write("=" * 80 + "\n")
    f.write("ANÁLISIS PROFUNDO: RESERVAS vs CONTRATOS (Feb 2026)\n")
    f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")

    conn_raw = get_conn('assetplan_rentas')
    cur = conn_raw.cursor(dictionary=True)

    f.write("─" * 60 + "\n")
    f.write("FUENTE 1: assetplan_rentas (Base cruda / producción)\n")
    f.write("─" * 60 + "\n\n")

    # 1a. Total reservas brutas
    cur.execute("SELECT COUNT(*) as total FROM reservas WHERE fecha BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'")
    raw_total = cur.fetchone()['total']
    f.write(f"1. Total Reservas Brutas (Feb 1-17): {raw_total}\n")

    # 1b. Reservas con caída
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as caidas,
            SUM(CASE WHEN ar.r_caida = 0 OR ar.r_caida IS NULL THEN 1 ELSE 0 END) as netas
        FROM reservas r
        LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
        WHERE r.fecha BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
    """)
    raw_detail = cur.fetchone()
    f.write(f"2. Desglose Reservas:\n")
    f.write(f"   - Brutas: {raw_detail['total']}\n")
    f.write(f"   - Caídas: {raw_detail['caidas']}\n")
    f.write(f"   - Netas (sin caídas): {raw_detail['netas']}\n\n")

    # 1c. Reservas por corredor activo (con coordinador)
    cur.execute("""
        SELECT 
            COUNT(*) as total_con_corredor
        FROM reservas r
        JOIN corredores c ON r.corredor_id = c.id
        JOIN users u ON c.coordinador_id = u.id
        LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
        WHERE r.fecha BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
          AND c.activo = 1
          AND u.email IS NOT NULL
          AND (ar.r_caida = 0 OR ar.r_caida IS NULL)
    """)
    raw_filtered = cur.fetchone()['total_con_corredor']
    f.write(f"3. Reservas Netas (activos + coordinador): {raw_filtered}\n")
    f.write(f"   ↑ ESTE es el número que muestra el dashboard actual (daily_stats)\n\n")

    # 1d. Reservas sin filtro de corredor activo
    cur.execute("""
        SELECT 
            COUNT(*) as total_sin_filtro
        FROM reservas r
        LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
        WHERE r.fecha BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
          AND (ar.r_caida = 0 OR ar.r_caida IS NULL)
    """)
    raw_all_net = cur.fetchone()['total_sin_filtro']
    f.write(f"4. Reservas Netas (TODOS los corredores): {raw_all_net}\n\n")

    conn_raw.close()

    # =============================================
    # PART 2: BI DATABASE (bi_assetplan)
    # =============================================
    conn_bi = get_conn('bi_assetplan')
    cur_bi = conn_bi.cursor(dictionary=True)

    f.write("─" * 60 + "\n")
    f.write("FUENTE 2: bi_assetplan (Base BI procesada)\n")
    f.write("─" * 60 + "\n\n")

    # 2a. Total contratos BI
    cur_bi.execute("SELECT COUNT(*) as total FROM bi_DimContratos WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'")
    bi_contracts = cur_bi.fetchone()['total']
    f.write(f"5. Total Contratos BI (bi_DimContratos): {bi_contracts}\n")

    # 2b. Contratos vigentes
    cur_bi.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN vigente = 1 THEN 1 ELSE 0 END) as vigentes,
            SUM(CASE WHEN vigente = 0 THEN 1 ELSE 0 END) as no_vigentes
        FROM bi_DimContratos 
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
    """)
    bi_detail = cur_bi.fetchone()
    f.write(f"6. Desglose Contratos BI:\n")
    f.write(f"   - Total: {bi_detail['total']}\n")
    f.write(f"   - Vigentes: {bi_detail['vigentes']}\n")
    f.write(f"   - No Vigentes: {bi_detail['no_vigentes']}\n\n")

    # 2c. Total reservas BI
    cur_bi.execute("SELECT COUNT(*) as total FROM bi_DimReservas WHERE fecha BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'")
    bi_reservas = cur_bi.fetchone()['total']
    f.write(f"7. Total Reservas BI (bi_DimReservas): {bi_reservas}\n")

    # 2d. Reservas sin contrato y sin caída
    cur_bi.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(reserva) as con_reserva,
            SUM(reserva_sin_contrato_no_caida) as sin_contrato_no_caida
        FROM bi_DimReservas 
        WHERE fecha BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
    """)
    bi_res_detail = cur_bi.fetchone()
    f.write(f"8. Desglose Reservas BI:\n")
    f.write(f"   - Total filas: {bi_res_detail['total']}\n")
    f.write(f"   - Con reserva (flag): {bi_res_detail['con_reserva']}\n")
    f.write(f"   - Sin contrato y no caída: {bi_res_detail['sin_contrato_no_caida']}\n\n")

    # 2e. Contratos por corredor (top 10)
    cur_bi.execute("""
        SELECT 
            nombre_corredor_id as corredor,
            COUNT(*) as contratos
        FROM bi_DimContratos 
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
          AND corredor_id IS NOT NULL
        GROUP BY nombre_corredor_id
        ORDER BY contratos DESC
        LIMIT 10
    """)
    f.write(f"9. Top 10 Corredores por Contratos (BI):\n")
    for row in cur_bi.fetchall():
        f.write(f"   {row['corredor']}: {row['contratos']}\n")

    # 2f. Contratos sin corredor
    cur_bi.execute("""
        SELECT COUNT(*) as total
        FROM bi_DimContratos 
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
          AND corredor_id IS NULL
    """)
    sin_corredor = cur_bi.fetchone()['total']
    f.write(f"\n10. Contratos SIN corredor asignado: {sin_corredor}\n")

    # 2g. Contratos con corredor
    cur_bi.execute("""
        SELECT COUNT(*) as total
        FROM bi_DimContratos 
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
          AND corredor_id IS NOT NULL
    """)
    con_corredor = cur_bi.fetchone()['total']
    f.write(f"11. Contratos CON corredor asignado: {con_corredor}\n\n")

    # 2h. Tipos de renovación
    cur_bi.execute("""
        SELECT 
            COALESCE(tipo_renovacion, 'NULL/NUEVO') as tipo,
            COUNT(*) as total
        FROM bi_DimContratos 
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
        GROUP BY tipo_renovacion
        ORDER BY total DESC
    """)
    f.write(f"12. Contratos por Tipo de Renovación:\n")
    for row in cur_bi.fetchall():
        f.write(f"   {row['tipo']}: {row['total']}\n")

    # 2i. Contratos heredados vs nuevos
    cur_bi.execute("""
        SELECT 
            CASE WHEN heredado = 1 THEN 'Heredado' ELSE 'Nuevo' END as tipo,
            COUNT(*) as total
        FROM bi_DimContratos 
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
        GROUP BY heredado
        ORDER BY total DESC
    """)
    f.write(f"\n13. Contratos Heredados vs Nuevos:\n")
    for row in cur_bi.fetchall():
        f.write(f"   {row['tipo']}: {row['total']}\n")

    # =============================================
    # PART 3: CROSS-REFERENCE
    # =============================================
    f.write("\n" + "─" * 60 + "\n")
    f.write("COMPARATIVA Y CONCLUSIONES\n")
    f.write("─" * 60 + "\n\n")

    f.write(f"Dashboard actual (reservas netas activos):     {raw_filtered}\n")
    f.write(f"Reservas BI (bi_DimReservas):                  {bi_reservas}\n")
    f.write(f"Contratos BI (bi_DimContratos):                {bi_contracts}\n")
    f.write(f"Contratos vigentes BI:                         {bi_detail['vigentes']}\n\n")

    f.write(f"META MENSUAL CONTRATOS:                        2.066\n")
    f.write(f"META MENSUAL RESERVAS:                         2.174\n\n")

    if bi_detail['vigentes']:
        pct_real = (int(bi_detail['vigentes']) / 2066) * 100
    else:
        pct_real = (bi_contracts / 2066) * 100
    pct_dashboard = (raw_filtered / 2066) * 100

    f.write(f"% Avance Real Contratos (vigentes):            {pct_real:.1f}%\n")
    f.write(f"% Avance Dashboard actual (reservas proxy):    {pct_dashboard:.1f}%\n")
    f.write(f"DIFERENCIA:                                    {pct_real - pct_dashboard:+.1f} puntos porcentuales\n\n")

    # 3a. Comparativa por corredor (top 5 con diferencia)
    f.write("14. Comparativa por Corredor (Reservas Raw vs Contratos BI):\n")

    conn_raw2 = get_conn('assetplan_rentas')
    cur_raw2 = conn_raw2.cursor(dictionary=True)
    cur_raw2.execute("""
        SELECT 
            CONCAT(c.nombre, ' ', c.apellido) as corredor,
            c.id as corredor_id,
            COUNT(r.id) as reservas_brutas,
            SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as caidas,
            COUNT(r.id) - SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as reservas_netas
        FROM corredores c
        LEFT JOIN reservas r ON c.id = r.corredor_id AND r.fecha BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
        LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
        WHERE c.activo = 1
        GROUP BY c.id, c.nombre, c.apellido
        HAVING reservas_brutas > 0
        ORDER BY reservas_netas DESC
        LIMIT 15
    """)
    raw_brokers = cur_raw2.fetchall()
    conn_raw2.close()

    cur_bi.execute("""
        SELECT 
            nombre_corredor_id as corredor,
            CAST(corredor_id AS UNSIGNED) as corredor_id,
            COUNT(*) as contratos,
            SUM(CASE WHEN vigente = 1 THEN 1 ELSE 0 END) as vigentes
        FROM bi_DimContratos 
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
          AND corredor_id IS NOT NULL
        GROUP BY nombre_corredor_id, corredor_id
        ORDER BY contratos DESC
    """)
    bi_brokers = {row['corredor_id']: row for row in cur_bi.fetchall()}

    f.write(f"{'Corredor':<35} {'Res.Netas':>10} {'Contratos':>10} {'Diff':>8}\n")
    f.write("-" * 70 + "\n")
    for rb in raw_brokers:
        cid = rb['corredor_id']
        bi_data = bi_brokers.get(cid, {})
        contratos = bi_data.get('contratos', 0)
        diff = contratos - rb['reservas_netas']
        f.write(f"{rb['corredor']:<35} {rb['reservas_netas']:>10} {contratos:>10} {diff:>+8}\n")

    conn_bi.close()

    f.write("\n" + "=" * 80 + "\n")
    f.write("FIN DEL ANÁLISIS\n")
    f.write("=" * 80 + "\n")

print("Analysis saved to:", output_path)
