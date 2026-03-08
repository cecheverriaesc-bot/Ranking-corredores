"""
Análisis filtrado por mes, usando bi_DimReservas para filtrar por fecha.
El objetivo es calcular cuántas reservas se hicieron en Marzo 2026 por corredor.
Luego cruzamos con bi_DimCorredores (activos) para tener nombre completo.
"""
import mysql.connector
import pandas as pd

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

# Primero revisemos el sample de bi_DimReservas para entender los campos
conn = bi()
df_sample = pd.read_sql("SELECT * FROM bi_DimReservas ORDER BY reserva_id DESC LIMIT 10", conn)
p("=== SAMPLE bi_DimReservas ===")
p(df_sample.to_string(index=False))
conn.close()

# Ver qué tablas tienen campo de corredor + fecha para el mes de marzo
conn = bi()
df_all_res = pd.read_sql("""
    SELECT fecha, COUNT(*) as total 
    FROM bi_DimReservas 
    WHERE fecha >= '2026-03-01' AND fecha < '2026-04-01'
    GROUP BY DATE(fecha)
    ORDER BY fecha
""", conn)
p("\n=== RESERVAS DÍA A DÍA MARZO 2026 ===")
p(df_all_res.to_string(index=False))
conn.close()

# Guardar
with open("scripts/analisis_v2_sample.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
print("\nGuardado en scripts/analisis_v2_sample.txt")
