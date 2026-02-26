import mysql.connector
import os
import json

def load_env_vars():
    env_vars = {}
    env_file_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def explore_db():
    env = load_env_vars()
    try:
        conn = mysql.connector.connect(
            host=env.get('DB_HOST'),
            user=env.get('DB_USER'),
            password=env.get('DB_PASSWORD'),
            port=int(env.get('DB_PORT', 3306)),
            database='bi_assetplan'
        )
        cursor = conn.cursor()
        
        print("--- bi_assetplan.bi_DimCorredores ---")
        cursor.execute("DESCRIBE bi_DimCorredores")
        for row in cursor.fetchall():
            print(row)
            
        print("\n--- assetplan_rentas.corredores ---")
        cursor.execute("USE assetplan_rentas")
        cursor.execute("DESCRIBE corredores")
        for row in cursor.fetchall():
            print(row)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_db()
