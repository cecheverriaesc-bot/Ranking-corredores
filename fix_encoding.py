import os

files_to_fix = [
    r"c:\Users\assetplan\Desktop\Nueva carpeta (3)\Ranking Enero 2026\Gobernanza_Ranking_2026\ranking-corredores-rm---dashboard\components\StrategicLab.tsx",
    r"c:\Users\assetplan\Desktop\Nueva carpeta (3)\Ranking Enero 2026\Gobernanza_Ranking_2026\ranking-corredores-rm---dashboard\components\SquadLaboratory.tsx"
]

for file_path in files_to_fix:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã±': 'ñ', 'Ã ': 'Á', 'Ã‰': 'É', 'Ã\x8d': 'Í', 'Ã“': 'Ó',
        'Ãš': 'Ú', 'Ã‘': 'Ñ', 'ðŸ †': '🏆', 'â€¢': '•', 'mÃ­n': 'mín',
        'Ã¯': 'ï', 'â€”': '—'
    }
    for k, v in replacements.items():
        content = content.replace(k, v)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed encoding for {os.path.basename(file_path)} using manual replacements.")
