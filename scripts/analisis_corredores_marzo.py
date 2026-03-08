"""
Análisis completo de Performance de Corredores — Marzo 2026
Fuente: bi_DimCorredores (métricas precalculadas por período)
"""
import mysql.connector
import pandas as pd
from datetime import datetime
import json
import os

YEAR = 2026
MONTH = 3

DB_CONFIG = dict(
    host="dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com",
    user="carlos.echeverria",
    password="JS5tyLBSMBdAdzAQ9r6UF2g7",
    port=3306
)

output = []
def p(t=""):
    print(t)
    output.append(str(t))

def bi():
    return mysql.connector.connect(**DB_CONFIG, database="bi_assetplan")

# ─────────────────────────────────────────────────────────────
# CONSULTA PRINCIPAL — Corredores de Marzo 2026
# ─────────────────────────────────────────────────────────────
conn = bi()

# Ver si hay filtro de mes/año en bi_DimCorredores
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM bi_DimCorredores")
total = cursor.fetchone()[0]
p(f"Total filas en bi_DimCorredores: {total}")

# Ver sample de corredor_id para entender la clave de fecha
cursor.execute("SELECT corredor_id, nombre_corredor, reserva, contrato_arriendos, cant_prospectos, cant_leads, coordinador, activo FROM bi_DimCorredores LIMIT 5")
for row in cursor.fetchall():
    p(f"  {row}")
conn.close()

# ─────────────────────────────────────────────────────────────
# META PROYECTADA — desde v4_goals.py logic (broker_goals.json)
# ─────────────────────────────────────────────────────────────
# Buscar broker_goals.json en el proyecto
goals_path = None
for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), "..")):
    for f in files:
        if f == "broker_goals.json":
            goals_path = os.path.join(root, f)

p(f"\nBroker goals path: {goals_path}")

goals_data = {}
if goals_path and os.path.exists(goals_path):
    with open(goals_path, "r", encoding="utf-8") as f:
        goals_data = json.load(f)
    p(f"Keys in goals: {list(goals_data.keys())[:10]}")
else:
    p("broker_goals.json no encontrado — usando proyección de historico.")

# ─────────────────────────────────────────────────────────────
# ANALISIS DE PERFORMANCE
# ─────────────────────────────────────────────────────────────
conn = bi()
df = pd.read_sql("""
    SELECT 
        corredor_id,
        nombre_corredor,
        coordinador,
        activo,
        reserva,
        contrato_arriendos,
        cant_prospectos,
        cant_leads,
        agendas_corredor,
        descartados_inactividad,
        descartados_no_contactado
    FROM bi_DimCorredores
    WHERE activo = 1
    ORDER BY reserva DESC
""", conn)
conn.close()

p(f"\n=== CORREDORES ACTIVOS: {len(df)} ===")
p(df[["nombre_corredor","coordinador","reserva","contrato_arriendos","cant_prospectos","cant_leads"]].to_string(index=False))

# ─────────────────────────────────────────────────────────────
# META EQUIPO — Carlos indicó: 1656 reservas / 1499 contratos
# ─────────────────────────────────────────────────────────────
META_RESERVAS = 1656
META_CONTRATOS = 1499
total_res = df["reserva"].sum()
total_cont = df["contrato_arriendos"].sum()
pct_res = total_res / META_RESERVAS * 100
pct_cont = total_cont / META_CONTRATOS * 100

p(f"\n=== AVANCE GLOBAL — MARZO 2026 ===")
p(f"Reservas:   {total_res:4d} / {META_RESERVAS} = {pct_res:.1f}%")
p(f"Contratos:  {total_cont:4d} / {META_CONTRATOS} = {pct_cont:.1f}%")

# ─────────────────────────────────────────────────────────────
# META INDIVIDUAL — Estimado proporcional
# ─────────────────────────────────────────────────────────────
n = len(df)
meta_ind_res = META_RESERVAS / n if n > 0 else 0
meta_ind_cont = META_CONTRATOS / n if n > 0 else 0

df["meta_est_res"] = meta_ind_res
df["meta_est_cont"] = meta_ind_cont
df["pct_res"] = (df["reserva"] / meta_ind_res * 100).round(1)
df["pct_cont"] = (df["contrato_arriendos"] / meta_ind_cont * 100).round(1)

p(f"\n=== RANKING INDIVIDUAL (Meta est. {meta_ind_res:.0f} res | {meta_ind_cont:.0f} cont por persona) ===")
df_sorted = df.sort_values("reserva", ascending=False)
p(f"{'#':>2} {'Corredor':<28} {'Res':>4} {'%Res':>6} {'Cont':>4} {'%Cont':>7}")
p("-" * 60)
for i, row in enumerate(df_sorted.itertuples(), 1):
    flag = " ⚠️ " if row.pct_res < 80 else ""
    p(f"{i:>2} {row.nombre_corredor:<28} {row.reserva:>4} {row.pct_res:>5.0f}% {row.contrato_arriendos:>4} {row.pct_cont:>6.0f}%{flag}")

# ─────────────────────────────────────────────────────────────
# EN RIESGO (< 80% meta)
# ─────────────────────────────────────────────────────────────
riesgosos = df[df["pct_res"] < 80].sort_values("pct_res")
p(f"\n=== CORREDORES EN RIESGO (< 80% meta) ===")
for row in riesgosos.itertuples():
    p(f"  ⚠️  {row.nombre_corredor}: {row.reserva:.0f} res ({row.pct_res:.0f}%)")

# ─────────────────────────────────────────────────────────────
# CASOS ESPECÍFICOS
# ─────────────────────────────────────────────────────────────
targets = ["Adriana", "Alexander", "Henmilys"]
p(f"\n=== SEGUIMIENTO ESPECÍFICO ===")
for t in targets:
    rows = df[df["nombre_corredor"].str.contains(t, case=False, na=False)]
    if not rows.empty:
        r = rows.iloc[0]
        p(f"  {r['nombre_corredor']}: {r['reserva']:.0f} res ({df.loc[df['nombre_corredor'].str.contains(t, case=False, na=False), 'pct_res'].values[0]:.0f}% meta) | {r['contrato_arriendos']:.0f} contratos | {r['cant_prospectos']:.0f} prospectos")
    else:
        p(f"  {t}: No encontrado con ese nombre")

# ─────────────────────────────────────────────────────────────
# PROYECCIÓN VARIABLE (escala: 80-100% = $2.000/décima, 100-110% = $4.000/décima)
# ─────────────────────────────────────────────────────────────
p(f"\n=== PROYECCIÓN DE VARIABLE ===")
p(f"{'Corredor':<28} {'%':>5} {'Variable Estimada':>20}")
p("-" * 55)

SUELDO_BASE = 800_000  # CLP estimado (ajustar si Carlos da el dato real)
RATE_80_100 = 2_000    # CLP por décima (0.1%) 80-100%
RATE_100_110 = 4_000   # CLP por décima 100-110%

for row in df_sorted.itertuples():
    pct = row.pct_res / 100  # Convertir a decimal
    variable = 0.0
    if pct >= 0.80:
        decimas_80_100 = min((pct - 0.80), 0.20) * 1000  # décimas entre 80-100%
        variable += decimas_80_100 * RATE_80_100
    if pct > 1.00:
        decimas_100_110 = min((pct - 1.00), 0.10) * 1000  # décimas entre 100-110%
        variable += decimas_100_110 * RATE_100_110
    
    p(f"  {row.nombre_corredor:<26} {row.pct_res:>5.1f}%  ${variable:>12,.0f}")

# Guardar a archivo
out_path = os.path.join(os.path.dirname(__file__), "analisis_marzo_2026.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(output))

p(f"\n✅ Guardado en: {out_path}")
