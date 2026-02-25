
import mysql.connector
import os
from dotenv import load_dotenv

# Use same strategy as etl_ranking.py to find .env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_options = [
    os.path.join(script_dir, "..", "..", "..", ".env"),  # Gobernanza_Ranking_2026/.env
    os.path.join(script_dir, "..", ".env.local"),         # dashboard/.env.local
    os.path.join(os.getcwd(), ".env")                     # Current working directory
]

print("🔍 Searching for .env file...")
env_loaded = False
for path in env_options:
    abs_path = os.path.abspath(path)
    exists = os.path.exists(abs_path)
    print(f"  Checking: {abs_path} | Exists: {exists}")
    if exists:
        load_dotenv(abs_path)
        print(f"✅ Loaded env from: {abs_path}")
        env_loaded = True
        break

if not env_loaded:
    print("❌ WARNING: No .env file found in expected paths")

print(f"\nDB_USER: {os.getenv('DB_USER')}")
print(f"DB_HOST: {os.getenv('DB_HOST')}")


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),  # Use host from .env, not hardcoded
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME", "assetplan_rentas")  # Use DB_NAME from .env
    )

def inspect():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("\n--- TABLES LIKE '%unidades%' ---")
        cursor.execute("SHOW TABLES LIKE '%unidades%'")
        for x in cursor.fetchall(): print(x)
        
        print("\n--- TABLES LIKE '%stock%' ---")
        cursor.execute("SHOW TABLES LIKE '%stock%'")
        for x in cursor.fetchall(): print(x)
        
        print("\n--- TABLES LIKE '%contrato%' ---")
        cursor.execute("SHOW TABLES LIKE '%contrato%'")
        for x in cursor.fetchall(): print(x)

        # Check 'unidades' columns if it exists
        print("\n--- COLUMNS IN 'unidades' ---")
        try:
            cursor.execute("DESCRIBE unidades")
            for x in cursor.fetchall(): print(f"{x[0]}")
        except:
            print("Table 'unidades' not found or error.")

        # Check 'leads' columns for logic validation
        print("\n--- COLUMNS IN 'leads' ---")
        cursor.execute("DESCRIBE leads")
        for x in cursor.fetchall(): print(f"{x[0]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    inspect()
