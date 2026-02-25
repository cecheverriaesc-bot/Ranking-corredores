
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv("c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/.env.local")

def get_conn(db):
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=db
    )

output_path = "c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/Gobernanza_Ranking_2026/ranking-corredores-rm---dashboard/calibration_results.txt"

# =============================================
# TABLA DE REFERENCIA DEL USUARIO (Feb 2026)
# =============================================
user_data = {
    # day: (contratos_aa, contratos_real, contratos_plan, reservas_aa, reservas_real, reservas_plan)
    1:  (0, 0, 0, 11, 24, 12),
    2:  (77, 86, 87, 81, 100, 91),
    3:  (147, 176, 166, 155, 181, 175),
    4:  (218, 254, 246, 240, 252, 271),
    5:  (303, 326, 342, 350, 326, 373),
    6:  (393, 411, 443, 438, 395, 473),
    7:  (393, 443, 443, 496, 435, 539),
    8:  (393, 412, 443, 514, 446, 559),
    9:  (463, 488, 522, 681, 519, 636),
    10: (538, 565, 606, 681, 584, 748),
    11: (616, 630, 694, 765, 666, 843),
    12: (709, 693, 799, 859, 732, 950),
    13: (824, 762, 928, 949, 806, 1052),
    14: (824, 762, 928, 992, 851, 1101),
    15: (824, 762, 928, 1013, 862, 1125),
    16: (906, 865, 1020, 1074, 925, 1194),
    17: (996, 865, 1121, 1154, 925, 1285),
    # Rows after 17 show future plan only
    28: (1647, 865, 1878, 1841, 925, 2086),
}

with open(output_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("CALIBRACIÓN: Dashboard vs Tabla Oficial (Feb 2026)\n")
    f.write("=" * 80 + "\n\n")

    # The user's Real data stops at day 16 → latest snapshot
    f.write("DATOS DE REFERENCIA (día 16, último dato real):\n")
    f.write(f"  Contratos Real:  865\n")
    f.write(f"  Reservas Real:   925\n")
    f.write(f"  Meta Contratos (fin mes):  1,878 (100%)\n")
    f.write(f"  Meta Reservas (fin mes):   2,086\n\n")

    # ── CALIBRATION 1: Try to match 865 contracts ──
    f.write("─" * 60 + "\n")
    f.write("CALIBRACIÓN CONTRATOS: Buscando query que dé ~865\n")
    f.write("─" * 60 + "\n\n")

    conn_bi = get_conn('bi_assetplan')
    cur = conn_bi.cursor(dictionary=True)

    # Cutoff: end of day Feb 16
    cutoff = '2026-02-16 23:59:59'
    start = '2026-02-01 00:00:00'

    queries = {
        "A) Todos los contratos": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}'
        """,
        "B) Contratos vigentes": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}' AND vigente = 1
        """,
        "C) Nuevos (sin renovación web)": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}' 
            AND (tipo_renovacion = 'Nuevo' OR tipo_renovacion IS NULL)
        """,
        "D) Nuevos con corredor": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}' 
            AND (tipo_renovacion = 'Nuevo' OR tipo_renovacion IS NULL)
            AND corredor_id IS NOT NULL
        """,
        "E) Nuevos vigentes": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}' 
            AND (tipo_renovacion = 'Nuevo' OR tipo_renovacion IS NULL)
            AND vigente = 1
        """,
        "F) Nuevos vigentes con corredor": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}' 
            AND (tipo_renovacion = 'Nuevo' OR tipo_renovacion IS NULL)
            AND vigente = 1 AND corredor_id IS NOT NULL
        """,
        "G) Solo tipo_renovacion = 'Nuevo'": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}' 
            AND tipo_renovacion = 'Nuevo'
        """,
        "H) tipo_renovacion = 'Nuevo' y vigente": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}' 
            AND tipo_renovacion = 'Nuevo' AND vigente = 1
        """,
        "I) tipo_renovacion = 'Nuevo' y NO heredado": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}' 
            AND tipo_renovacion = 'Nuevo' AND heredado = 0
        """,
        "J) Nuevos con corredor y no heredados": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}' 
            AND tipo_renovacion = 'Nuevo' AND heredado = 0 AND corredor_id IS NOT NULL
        """,
        "K) Nuevos vigentes no heredados": f"""
            SELECT COUNT(*) as total FROM bi_DimContratos 
            WHERE created_at BETWEEN '{start}' AND '{cutoff}' 
            AND tipo_renovacion = 'Nuevo' AND heredado = 0 AND vigente = 1
        """,
    }

    f.write(f"{'Query':<45} {'Resultado':>10} {'Diff vs 865':>12}\n")
    f.write("-" * 70 + "\n")
    for name, query in queries.items():
        cur.execute(query)
        result = cur.fetchone()['total']
        diff = result - 865
        marker = " ← MATCH!" if abs(diff) <= 5 else ""
        f.write(f"{name:<45} {result:>10} {diff:>+12}{marker}\n")

    # ── CALIBRATION 2: Try to match 925 reservas ──
    f.write("\n\n" + "─" * 60 + "\n")
    f.write("CALIBRACIÓN RESERVAS: Buscando query que dé ~925\n")
    f.write("─" * 60 + "\n\n")

    # From raw db
    conn_raw = get_conn('assetplan_rentas')
    cur_raw = conn_raw.cursor(dictionary=True)

    res_queries = {
        "A) Raw: Todas las reservas": f"""
            SELECT COUNT(*) as total FROM reservas 
            WHERE fecha BETWEEN '{start}' AND '{cutoff}'
        """,
        "B) Raw: Netas (sin caída)": f"""
            SELECT COUNT(*) as total FROM reservas r
            LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
            WHERE r.fecha BETWEEN '{start}' AND '{cutoff}'
            AND (ar.r_caida = 0 OR ar.r_caida IS NULL)
        """,
        "C) Raw: Netas + activo + coord": f"""
            SELECT COUNT(*) as total FROM reservas r
            JOIN corredores c ON r.corredor_id = c.id
            JOIN users u ON c.coordinador_id = u.id
            LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
            WHERE r.fecha BETWEEN '{start}' AND '{cutoff}'
            AND c.activo = 1 AND u.email IS NOT NULL
            AND (ar.r_caida = 0 OR ar.r_caida IS NULL)
        """,
        "D) Raw: Netas SIN filtro activo": f"""
            SELECT COUNT(*) as total FROM reservas r
            JOIN corredores c ON r.corredor_id = c.id
            LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
            WHERE r.fecha BETWEEN '{start}' AND '{cutoff}'
            AND (ar.r_caida = 0 OR ar.r_caida IS NULL)
        """,
    }

    f.write(f"{'Query':<45} {'Resultado':>10} {'Diff vs 925':>12}\n")
    f.write("-" * 70 + "\n")
    for name, query in res_queries.items():
        cur_raw.execute(query)
        result = cur_raw.fetchone()['total']
        diff = result - 925
        marker = " ← MATCH!" if abs(diff) <= 5 else ""
        f.write(f"{name:<45} {result:>10} {diff:>+12}{marker}\n")
    conn_raw.close()

    # BI reservas
    bi_res_queries = {
        "E) BI: bi_DimReservas total": f"""
            SELECT COUNT(*) as total FROM bi_DimReservas 
            WHERE fecha BETWEEN '{start}' AND '{cutoff}'
        """,
        "F) BI: bi_DimReservas con flag reserva=1": f"""
            SELECT SUM(reserva) as total FROM bi_DimReservas 
            WHERE fecha BETWEEN '{start}' AND '{cutoff}'
        """,
    }

    for name, query in bi_res_queries.items():
        cur.execute(query)
        result = cur.fetchone()['total'] or 0
        diff = result - 925
        marker = " ← MATCH!" if abs(diff) <= 5 else ""
        f.write(f"{name:<45} {result:>10} {diff:>+12}{marker}\n")

    # ── CALIBRATION 3: Day-by-day comparison ──
    f.write("\n\n" + "─" * 60 + "\n")
    f.write("COMPARATIVA DIARIA: User Table vs BI Queries\n")
    f.write("─" * 60 + "\n\n")

    # Get cumulative contracts per day (Nuevos, no heredados, vigentes)
    cur.execute(f"""
        SELECT DATE(created_at) as dia, COUNT(*) as daily
        FROM bi_DimContratos
        WHERE created_at BETWEEN '{start}' AND '{cutoff}'
        AND tipo_renovacion = 'Nuevo' AND vigente = 1
        GROUP BY DATE(created_at)
        ORDER BY dia
    """)
    daily_contracts = []
    cumulative = 0
    for row in cur.fetchall():
        cumulative += row['daily']
        daily_contracts.append((str(row['dia']), row['daily'], cumulative))

    # Get cumulative reservas per day from BI
    cur.execute(f"""
        SELECT DATE(fecha) as dia, COUNT(*) as daily
        FROM bi_DimReservas
        WHERE fecha BETWEEN '{start}' AND '{cutoff}'
        GROUP BY DATE(fecha)
        ORDER BY dia
    """)
    daily_reservas = []
    cumulative_r = 0
    for row in cur.fetchall():
        cumulative_r += row['daily']
        daily_reservas.append((str(row['dia']), row['daily'], cumulative_r))

    f.write(f"{'Día':<6} {'C.User':>8} {'C.BI':>8} {'Diff':>6}  |  {'R.User':>8} {'R.BI':>8} {'Diff':>6}\n")
    f.write("-" * 65 + "\n")
    
    # Build lookup maps
    bi_c_map = {d[0]: d[2] for d in daily_contracts}
    bi_r_map = {d[0]: d[2] for d in daily_reservas}

    for day in range(1, 17):
        day_str = f"2026-02-{day:02d}"
        if day in user_data:
            c_user = user_data[day][1]  # contratos real
            r_user = user_data[day][4]  # reservas real
            c_bi = bi_c_map.get(day_str, 0)
            r_bi = bi_r_map.get(day_str, 0)
            c_diff = c_bi - c_user
            r_diff = r_bi - r_user
            f.write(f"  {day:>2}   {c_user:>8} {c_bi:>8} {c_diff:>+6}  |  {r_user:>8} {r_bi:>8} {r_diff:>+6}\n")

    conn_bi.close()

    f.write("\n" + "=" * 80 + "\n")
    f.write("FIN CALIBRACIÓN\n")
    f.write("=" * 80 + "\n")

print("Calibration saved to:", output_path)
