"""
Auditoría rápida del constants.ts generado.
Verifica los totales, metas y número de corredores por cada mes.
"""
import json
import re

with open("constants.ts", encoding="utf-8") as f:
    raw = f.read()

# Extraer el objeto MONTHLY_DATA
match = re.search(r"export const MONTHLY_DATA.*?=\s*(\{.*?\});\s*\n\n", raw, re.DOTALL)
if not match:
    print("ERROR: No se pudo extraer MONTHLY_DATA")
    exit(1)

data = json.loads(match.group(1))

print("=" * 60)
print("AUDITORÍA COMPLETA - MONTHLY_DATA")
print("=" * 60)

for mes_id, mes in data.items():
    goal = mes.get("goal", 0)
    contract_goal = mes.get("contract_goal", 0)
    reservation_goal = mes.get("reservation_goal", 0)
    ranking = mes.get("ranking", [])
    others = mes.get("others", [])
    daily_stats = mes.get("daily_stats", [])
    daily_goals = mes.get("daily_goals", {})
    history = mes.get("history", {})
    total_2025 = mes.get("total_2025_ytd", 0)

    # Totales del ranking
    total_val = sum(c["val"] for c in ranking)
    total_contracts = sum(c["contracts"] for c in ranking)
    total_leads = sum(c["leads"] for c in ranking)
    total_fallen = sum(c["fallen"] for c in ranking)
    sin_dato = [c["name"] for c in ranking if c["val"] == 0]
    cero_leads = [c["name"] for c in ranking if c["leads"] == 0]
    cero_contracts = [c["name"] for c in ranking if c["contracts"] == 0 and c["val"] > 5]

    print(f"\n{'=' * 60}")
    print(f"  MES: {mes_id}")
    print(f"{'=' * 60}")
    print(f"  Meta Contratos       : {contract_goal}")
    print(f"  Meta Reservas (smart): {reservation_goal}")
    print(f"  Goal (variable)      : {goal}")
    print(f"")
    print(f"  Freelance (ranking)  : {len(ranking)} corredores")
    print(f"  Institucional (otros): {len(others)} corredores")
    print(f"  TOTAL corredores     : {len(ranking) + len(others)}")
    print(f"")
    print(f"  Reservas netas TOTAL : {total_val}")
    print(f"  Caídas TOTAL         : {total_fallen}")
    print(f"  Contratos TOTAL      : {total_contracts}")
    print(f"  Leads TOTAL          : {total_leads}")
    print(f"  % meta reservas      : {round((total_val/reservation_goal)*100, 1)}% {'✅' if total_val/reservation_goal >= 1 else '⚠️'}" if reservation_goal > 0 else "  % meta reservas      : N/A")
    print(f"")
    print(f"  Días con stats diarios: {len(daily_stats)}")
    print(f"  Días metas diarias   : {len(daily_goals)}")
    print(f"  Total 2025 YTD       : {total_2025}")
    print(f"  Corredores historia  : {len(history)}")
    print(f"")
    if sin_dato:
        print(f"  ⚠️  Con 0 reservas ({len(sin_dato)}): {', '.join(sin_dato[:5])}{'...' if len(sin_dato) > 5 else ''}")
    if cero_contracts:
        print(f"  ⚠️  Con reservas pero 0 contratos ({len(cero_contracts)}): {', '.join(cero_contracts[:5])}")
    if cero_leads:
        print(f"  ⚠️  Con 0 leads ({len(cero_leads)}): {', '.join(cero_leads[:5])}{'...' if len(cero_leads) > 5 else ''}")

    # Top 5
    top5 = sorted(ranking, key=lambda x: x["val"], reverse=True)[:5]
    print(f"\n  Top 5 Reservas:")
    for i, c in enumerate(top5, 1):
        pct = round((c["val"] / c["personalMeta"]) * 100, 1) if c.get("personalMeta", 0) > 0 else 0
        print(f"    {i}. {c['name']:<30} val={c['val']:>4}  meta={c['personalMeta']:>4}  {pct:>6}%  leads={c['leads']:>5}")

print("\n")
# Extraer LAST_UPDATE
lu_match = re.search(r"export const LAST_UPDATE = '(.+?)'", raw)
ldu_match = re.search(r"export const LAST_DB_UPDATE = '(.+?)'", raw)
print(f"LAST_UPDATE   : {lu_match.group(1) if lu_match else 'N/A'}")
print(f"LAST_DB_UPDATE: {ldu_match.group(1) if ldu_match else 'N/A'}")
