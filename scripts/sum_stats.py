
import json

def sum_feb():
    with open('constants.ts', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find start of MONTHLY_DATA
    start_index = content.find('export const MONTHLY_DATA')
    # This is a bit hacky, but let's just find the February daily_stats block
    feb_start = content.find('"2026-02": {')
    feb_daily_start = content.find('"daily_stats": [', feb_start)
    feb_daily_end = content.find('],', feb_daily_start)
    
    json_chunk = content[feb_daily_start + 15 : feb_daily_end + 1]
    stats = json.loads(json_chunk)
    
    total = sum(s['count'] for s in stats)
    print(f"Total Reservas Dashboard (Feb): {total}")

if __name__ == "__main__":
    sum_feb()
