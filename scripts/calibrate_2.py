
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

# User reference data (cumulative)
user_contratos = {
    1: 0, 2: 86, 3: 176, 4: 254, 5: 326, 6: 411, 7: 443, 8: 412,
    9: 488, 10: 565, 11: 630, 12: 693, 13: 762, 14: 762, 15: 762, 16: 865
}

user_reservas = {
    1: 24, 2: 100, 3: 181, 4: 252, 5: 326, 6: 395, 7: 435, 8: 446,
    9: 519, 10: 584, 11: 666, 12: 732, 13: 806, 14: 851, 15: 862, 16: 925
}

with open(output_path, 'a', encoding='utf-8') as f:
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("CALIBRACIÓN PARTE 2: Fuente RAW (assetplan_rentas)\n")
    f.write("=" * 80 + "\n\n")

    conn_raw = get_conn('assetplan_rentas')
    cur = conn_raw.cursor(dictionary=True)

    # Check what tables exist for contratos
    cur.execute("SHOW TABLES LIKE '%contrato%'")
    f.write("Tablas con 'contrato' en assetplan_rentas:\n")
    for t in cur.fetchall():
        f.write(f"  - {list(t.values())[0]}\n")

    # Try contrato_arriendos table
    f.write("\n── Tabla: contrato_arriendos ──\n")
    try:
        cur.execute("DESCRIBE contrato_arriendos")
        cols = cur.fetchall()
        date_cols = [c for c in cols if 'date' in c['Type'].lower() or 'time' in c['Type'].lower() 
                     or 'fecha' in c['Field'].lower() or 'created' in c['Field'].lower()]
        f.write("Columnas de fecha encontradas:\n")
        for c in date_cols:
            f.write(f"  {c['Field']} ({c['Type']})\n")
        
        # Count contracts by day, cumulative
        f.write("\nContratos por día (assetplan_rentas.contrato_arriendos):\n")
        
        # Try different date fields
        for date_field in ['created_at', 'fecha_inicio']:
            try:
                cur.execute(f"""
                    SELECT DATE({date_field}) as dia, COUNT(*) as daily
                    FROM contrato_arriendos
                    WHERE {date_field} BETWEEN '2026-02-01' AND '2026-02-16 23:59:59'
                    GROUP BY DATE({date_field})
                    ORDER BY dia
                """)
                rows = cur.fetchall()
                if rows:
                    f.write(f"\n  Usando campo: {date_field}\n")
                    cumulative = 0
                    f.write(f"  {'Día':<6} {'Diario':>8} {'Acum':>8} {'User':>8} {'Diff':>8}\n")
                    f.write("  " + "-" * 42 + "\n")
                    for row in rows:
                        cumulative += row['daily']
                        day_num = row['dia'].day
                        user_val = user_contratos.get(day_num, '-')
                        diff = cumulative - user_val if isinstance(user_val, int) else '-'
                        marker = " ←" if isinstance(diff, int) and abs(diff) <= 5 else ""
                        f.write(f"  {day_num:>4}   {row['daily']:>8} {cumulative:>8} {user_val:>8} {diff:>8}{marker}\n")
            except Exception as e:
                f.write(f"  Error con {date_field}: {e}\n")

        # Try with filters similar to ETL
        f.write("\n\n── Contratos con filtros ETL (activo, coordinador, neto) ──\n")
        for date_field in ['created_at']:
            try:
                cur.execute(f"""
                    SELECT DATE(ca.{date_field}) as dia, COUNT(*) as daily
                    FROM contrato_arriendos ca
                    JOIN corredores c ON ca.corredor_id = c.id
                    JOIN users u ON c.coordinador_id = u.id
                    WHERE ca.{date_field} BETWEEN '2026-02-01' AND '2026-02-16 23:59:59'
                      AND c.activo = 1
                      AND u.email IS NOT NULL
                    GROUP BY DATE(ca.{date_field})
                    ORDER BY dia
                """)
                rows = cur.fetchall()
                if rows:
                    f.write(f"\n  Usando campo: ca.{date_field} + activo + coord\n")
                    cumulative = 0
                    f.write(f"  {'Día':<6} {'Diario':>8} {'Acum':>8} {'User':>8} {'Diff':>8}\n")
                    f.write("  " + "-" * 42 + "\n")
                    for row in rows:
                        cumulative += row['daily']
                        day_num = row['dia'].day
                        user_val = user_contratos.get(day_num, '-')
                        diff = cumulative - user_val if isinstance(user_val, int) else '-'
                        marker = " ←" if isinstance(diff, int) and abs(diff) <= 5 else ""
                        f.write(f"  {day_num:>4}   {row['daily']:>8} {cumulative:>8} {user_val:>8} {diff:>8}{marker}\n")
            except Exception as e:
                f.write(f"  Error: {e}\n")

    except Exception as e:
        f.write(f"Error: {e}\n")

    # Also check the existing ETL query logic
    f.write("\n\n── Verificación: Query del ETL actual ──\n")
    try:
        # This mimics what fetch_ranking_data does in etl_ranking.py
        cur.execute("""
            SELECT DATE(r.fecha) as dia, 
                   COUNT(r.id) as res_brutas,
                   SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as caidas,
                   COUNT(r.id) - SUM(CASE WHEN ar.r_caida = 1 THEN 1 ELSE 0 END) as res_netas
            FROM reservas r
            JOIN corredores c ON r.corredor_id = c.id
            JOIN users u ON c.coordinador_id = u.id
            LEFT JOIN asignacion_reservas ar ON r.id = ar.reserva_id
            WHERE r.fecha BETWEEN '2026-02-01' AND '2026-02-16 23:59:59'
              AND c.activo = 1
              AND u.email IS NOT NULL
            GROUP BY DATE(r.fecha)
            ORDER BY dia
        """)
        rows = cur.fetchall()
        f.write(f"\n  Reservas ETL (netas activos) por día:\n")
        cumulative = 0
        f.write(f"  {'Día':<6} {'Diario':>8} {'Acum':>8} {'User':>8} {'Diff':>8}\n")
        f.write("  " + "-" * 42 + "\n")
        for row in rows:
            cumulative += row['res_netas']
            day_num = row['dia'].day
            user_val = user_reservas.get(day_num, '-')
            diff = cumulative - user_val if isinstance(user_val, int) else '-'
            marker = " ←" if isinstance(diff, int) and abs(diff) <= 5 else ""
            f.write(f"  {day_num:>4}   {row['res_netas']:>8} {cumulative:>8} {user_val:>8} {diff:>8}{marker}\n")
    except Exception as e:
        f.write(f"  Error: {e}\n")

    conn_raw.close()

    f.write("\n" + "=" * 80 + "\n")
    f.write("FIN CALIBRACIÓN PARTE 2\n")
    f.write("=" * 80 + "\n")

print("Calibration part 2 saved.")
