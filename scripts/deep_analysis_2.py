
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

output_path = "c:/Users/assetplan/Desktop/Nueva carpeta (3)/Ranking Enero 2026/Gobernanza_Ranking_2026/ranking-corredores-rm---dashboard/analysis_results.txt"

with open(output_path, 'a', encoding='utf-8') as f:
    conn_bi = get_conn('bi_assetplan')
    cur = conn_bi.cursor(dictionary=True)

    f.write("\n\n" + "=" * 80 + "\n")
    f.write("ANÁLISIS COMPLEMENTARIO: ¿Por qué Contratos > Reservas?\n")
    f.write("=" * 80 + "\n\n")

    # 1. Contratos sin lead vinculado (pueden ser renovaciones internas)
    cur.execute("""
        SELECT 
            CASE 
                WHEN lead_id IS NULL OR lead_id = '' THEN 'Sin Lead'
                ELSE 'Con Lead'
            END as tipo,
            COUNT(*) as total
        FROM bi_DimContratos
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
        GROUP BY tipo
    """)
    f.write("1. Contratos por presencia de Lead:\n")
    for row in cur.fetchall():
        f.write(f"   {row['tipo']}: {row['total']}\n")

    # 2. Contratos por tipo: Nuevo vs Renovación (desglose detallado)
    cur.execute("""
        SELECT 
            COALESCE(tipo_renovacion, 'Nuevo') as tipo,
            CASE WHEN corredor_id IS NULL THEN 'Sin Corredor' ELSE 'Con Corredor' END as corredor_status,
            COUNT(*) as total
        FROM bi_DimContratos
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
        GROUP BY tipo, corredor_status
        ORDER BY tipo, corredor_status
    """)
    f.write("\n2. Contratos: Tipo × Corredor:\n")
    f.write(f"   {'Tipo':<25} {'Corredor Status':<20} {'Total':>8}\n")
    f.write("   " + "-" * 55 + "\n")
    for row in cur.fetchall():
        f.write(f"   {row['tipo']:<25} {row['corredor_status']:<20} {row['total']:>8}\n")

    # 3. Contratos "Nuevo" con corredor = los que importan para el ranking
    cur.execute("""
        SELECT COUNT(*) as total
        FROM bi_DimContratos
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
          AND tipo_renovacion = 'Nuevo'
          AND corredor_id IS NOT NULL
    """)
    nuevos_con_corredor = cur.fetchone()['total']
    f.write(f"\n3. Contratos NUEVOS con corredor asignado: {nuevos_con_corredor}\n")
    f.write(f"   ↑ ESTOS son los contratos que deberían contar para el Ranking\n")

    # 4. Distribución diaria de contratos vs reservas
    f.write("\n4. Distribución Diaria (Feb 2026):\n")
    f.write(f"   {'Fecha':<12} {'Reservas BI':>12} {'Contratos BI':>14} {'Ratio C/R':>10}\n")
    f.write("   " + "-" * 50 + "\n")
    
    cur.execute("""
        SELECT 
            DATE(fecha) as dia,
            COUNT(*) as total
        FROM bi_DimReservas
        WHERE fecha BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
        GROUP BY DATE(fecha)
        ORDER BY dia
    """)
    reservas_diarias = {str(row['dia']): row['total'] for row in cur.fetchall()}

    cur.execute("""
        SELECT 
            DATE(created_at) as dia,
            COUNT(*) as total
        FROM bi_DimContratos
        WHERE created_at BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
        GROUP BY DATE(created_at)
        ORDER BY dia
    """)
    contratos_diarios = cur.fetchall()

    for row in contratos_diarios:
        dia_str = str(row['dia'])
        res = reservas_diarias.get(dia_str, 0)
        con = row['total']
        ratio = f"{con/res:.2f}" if res > 0 else "N/A"
        f.write(f"   {dia_str:<12} {res:>12} {con:>14} {ratio:>10}\n")

    # 5. ¿Cuántas reservas se convirtieron en contrato?
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(reserva_sin_contrato_no_caida) as pendientes
        FROM bi_DimReservas
        WHERE fecha BETWEEN '2026-02-01' AND '2026-02-17 23:59:59'
    """)
    res_status = cur.fetchone()
    convertidas = res_status['total'] - (res_status['pendientes'] or 0)
    f.write(f"\n5. Estado de Reservas BI:\n")
    f.write(f"   Total reservas:                    {res_status['total']}\n")
    f.write(f"   Sin contrato y no caída (pend.):   {res_status['pendientes']}\n")
    f.write(f"   Ya convertidas o caídas:           {convertidas}\n")

    # 6. Meta real: ¿qué se debería rastrear?
    f.write(f"\n\n" + "─" * 60 + "\n")
    f.write(f"CONCLUSIÓN ESTRATÉGICA\n")
    f.write(f"─" * 60 + "\n\n")
    f.write(f"La META de 2.066 es de CONTRATOS (no reservas).\n")
    f.write(f"Los 1.323 contratos totales incluyen:\n")
    f.write(f"  - 1.145 Nuevos (contratos de arriendo nuevos)\n")
    f.write(f"  - 178 Renovaciones Web (no vienen de reservas de corredor)\n\n")
    f.write(f"Para el RANKING de corredores, lo relevante son los\n")
    f.write(f"contratos NUEVOS con corredor asignado: {nuevos_con_corredor}\n\n")
    f.write(f"Para el avance ESTRATÉGICO de la empresa, lo relevante\n")
    f.write(f"son los 1.323 contratos totales (o 1.313 vigentes).\n\n")
    f.write(f"RECOMENDACIÓN:\n")
    f.write(f"  - Header Operativo: Seguir usando Reservas (operación diaria)\n")
    f.write(f"  - Header Estratégico: Usar Contratos TOTALES vigentes de BI\n")
    f.write(f"  - Ranking individual: Usar contratos NUEVOS con corredor\n")

    conn_bi.close()

print("Complementary analysis appended.")
