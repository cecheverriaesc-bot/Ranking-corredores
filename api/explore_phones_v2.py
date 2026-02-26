import mysql.connector
import os

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
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        env_vars[parts[0].strip()] = parts[1].strip()
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
        
        print("COLUMNS IN bi_assetplan.bi_DimCorredores:")
        cursor.execute("DESCRIBE bi_DimCorredores")
        cols = [row[0] for row in cursor.fetchall()]
        print(", ".join(cols))
            
        print("\nCOLUMNS IN assetplan_rentas.corredores:")
        cursor.execute("USE assetplan_rentas")
        cursor.execute("DESCRIBE corredores")
        cols = [row[0] for row in cursor.fetchall()]
        print(", ".join(cols))
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_db()
