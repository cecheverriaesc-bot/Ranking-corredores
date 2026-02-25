import re

with open('constants.ts', 'r', encoding='utf-8') as f:
    data = f.read()

contracts = re.findall(r'"contracts": (\d+)', data)
print(f"Total entries con 'contracts': {len(contracts)}")
total = sum(int(c) for c in contracts)
print(f"Suma total contratos: {total}")
print(f"contract_goal presente: {'contract_goal' in data}")

# Check Feb data specifically
feb_section = data[data.find('"2026-02"'):]
feb_contracts = re.findall(r'"contracts": (\d+)', feb_section[:50000])
feb_total = sum(int(c) for c in feb_contracts)
print(f"Contratos Feb: {len(feb_contracts)} entries, total: {feb_total}")

# Sanity check: contract_goal values
goals = re.findall(r'"contract_goal": (\d+)', data)
print(f"contract_goal values: {goals}")
