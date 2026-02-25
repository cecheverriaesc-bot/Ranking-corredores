
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

# User reference (cumulative)
user_contratos = {
    1: 0, 2: 86, 3: 176, 4: 254, 5: 326, 6: 411, 7: 443, 8: 412,
    9: 488, 10: 565, 11: 630, 12: 693, 13: 762, 14: 762, 15: 762, 16: 865
}

with open(output_path, 'a', encoding='utf-8') as f:
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("CALIBRACIÓN PARTE 3: Contratos con campo 'created'\n")
    f.write("=" * 80 + "\n\n")

    conn_raw = get_conn('assetplan_rentas')
    cur = conn_raw.cursor(dictionary=True)

    # ── Test 1: created (datetime) sin filtros ──
    queries_raw = {
        "A) created, sin filtros": """
            SELECT DATE(created) as dia, COUNT(*) as daily
            FROM contrato_arriendos
            WHERE created BETWEEN '2026-02-01' AND '2026-02-16 23:59:59'
            GROUP BY DATE(created) ORDER BY dia
        """,
        "B) created + activo + coord": """
            SELECT DATE(ca.created) as dia, COUNT(*) as daily
            FROM contrato_arriendos ca
            JOIN corredores c ON ca.corredor_id = c.id
            JOIN users u ON c.coordinador_id = u.id
            WHERE ca.created BETWEEN '2026-02-01' AND '2026-02-16 23:59:59'
              AND c.activo = 1 AND u.email IS NOT NULL
            GROUP BY DATE(ca.created) ORDER BY dia
        """,
        "C) created + corredor_id IS NOT NULL": """
            SELECT DATE(created) as dia, COUNT(*) as daily
            FROM contrato_arriendos
            WHERE created BETWEEN '2026-02-01' AND '2026-02-16 23:59:59'
              AND corredor_id IS NOT NULL
            GROUP BY DATE(created) ORDER BY dia
        """,
    }

    for name, query in queries_raw.items():
        try:
            cur.execute(query)
            rows = cur.fetchall()
            if rows:
                f.write(f"\n  {name}\n")
                cumulative = 0
                f.write(f"  {'Día':>4} {'Diario':>8} {'Acum':>8} {'User':>8} {'Diff':>8}\n")
                f.write("  " + "-" * 42 + "\n")
                for row in rows:
                    cumulative += row['daily']
                    day_num = row['dia'].day
                    user_val = user_contratos.get(day_num, '-')
                    diff = cumulative - user_val if isinstance(user_val, int) else '-'
                    marker = " ← MATCH" if isinstance(diff, int) and abs(diff) <= 5 else ""
                    f.write(f"  {day_num:>4} {row['daily']:>8} {cumulative:>8} {user_val:>8} {diff:>+8}{marker}\n")
                f.write(f"  Total acumulado: {cumulative}\n")
        except Exception as e:
            f.write(f"  {name}: Error: {e}\n")

    # ── Test vigencia: contrato_arriendo_vigentes ──
    f.write("\n\n── Tabla contrato_arriendo_vigentes ──\n")
    try:
        cur.execute("DESCRIBE contrato_arriendo_vigentes")
        cols = cur.fetchall()
        f.write("Columnas:\n")
        for c in cols:
            f.write(f"  {c['Field']} ({c['Type']})\n")
    except Exception as e:
        f.write(f"Error: {e}\n")

    # ── Check: what does the ETL currently use for "val" (ranking value)? ──
    f.write("\n\n── ¿Qué usa el ETL para el valor del ranking? ──\n")
    # Look at "gross_val" and "fallen_val" in the ETL - these come from reservas, not contratos
    # Let's check the actual ETL query
    f.write("El ETL actual usa reservas (bruto - caídas) como 'val'.\n")
    f.write("Esto es DIFERENTE de contratos.\n")
    f.write("La tabla oficial del usuario muestra CONTRATOS = 865.\n")
    f.write("Nuestro dashboard muestra RESERVAS = 921.\n\n")

    # ── Try BI with corredor filter, day by day ──
    f.write("\n── BI: bi_DimContratos NUEVOS con corredor (día a día) ──\n")
    conn_bi = get_conn('bi_assetplan')
    cur_bi = conn_bi.cursor(dictionary=True)

    cur_bi.execute("""
        SELECT DATE(created_at) as dia, COUNT(*) as daily
        FROM bi_DimContratos
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-16 23:59:59'
          AND tipo_renovacion = 'Nuevo'
          AND corredor_id IS NOT NULL
        GROUP BY DATE(created_at)
        ORDER BY dia
    """)
    rows = cur_bi.fetchall()
    cumulative = 0
    f.write(f"  {'Día':>4} {'Diario':>8} {'Acum':>8} {'User':>8} {'Diff':>8}\n")
    f.write("  " + "-" * 42 + "\n")
    for row in rows:
        cumulative += row['daily']
        day_num = row['dia'].day
        user_val = user_contratos.get(day_num, '-')
        diff = cumulative - user_val if isinstance(user_val, int) else '-'
        marker = " ← MATCH" if isinstance(diff, int) and abs(diff) <= 5 else ""
        f.write(f"  {day_num:>4} {row['daily']:>8} {cumulative:>8} {user_val:>8} {diff:>+8}{marker}\n")
    f.write(f"  Total: {cumulative}\n")

    # ── Try BI vigentes day-by-day (vigente can change over time) ──
    # Note: user data DECREASES on some days (day 8: 443→412), suggesting cancellations
    # Try counting vigente=1 contratos up to each day instead of cumulative sum
    f.write("\n\n── BI: Contratos vigentes ACUMULADOS hasta cada día ──\n")
    for day_num in sorted(user_contratos.keys()):
        day_end = f"2026-02-{day_num:02d} 23:59:59"
        cur_bi.execute(f"""
            SELECT COUNT(*) as total
            FROM bi_DimContratos
            WHERE created_at BETWEEN '2026-02-01' AND '{day_end}'
              AND tipo_renovacion = 'Nuevo'
              AND corredor_id IS NOT NULL
              AND vigente = 1
        """)
        bi_val = cur_bi.fetchone()['total']
        user_val = user_contratos[day_num]
        diff = bi_val - user_val
        marker = " ← MATCH" if abs(diff) <= 5 else ""
        f.write(f"  Día {day_num:>2}: BI={bi_val:>6}  User={user_val:>6}  Diff={diff:>+6}{marker}\n")

    conn_bi.close()
    conn_raw.close()

    f.write("\n" + "=" * 80 + "\n")
    f.write("FIN CALIBRACIÓN PARTE 3\n")
    f.write("=" * 80 + "\n")

print("Calibration part 3 saved.")
