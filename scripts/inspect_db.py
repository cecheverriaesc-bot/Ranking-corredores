
import mysql.connector
import os

print("=" * 70)
print("DATABASE SCHEMA INSPECTOR - Manual .env Parser")
print("=" * 70)

# Manual .env loading (python-dotenv is having issues)
env_vars = {}
env_file_path = r"c:\Users\assetplan\Desktop\Ranking Enero 2026\Gobernanza_Ranking_2026\.env"

print(f"\n📂 Reading .env from: {env_file_path}")
print(f"   File exists: {os.path.exists(env_file_path)}")

if os.path.exists(env_file_path):
    with open(env_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    print(f"   ✅ Loaded {len(env_vars)} variables\n")
else:
    print("   ❌ File not found!\n")
    exit(1)

print("-" * 70)
print(f"DB_USER: {env_vars.get('DB_USER', 'NOT FOUND')}")
print(f"DB_HOST: {env_vars.get('DB_HOST', 'NOT FOUND')}")
print(f"DB_NAME: {env_vars.get('DB_NAME', 'NOT FOUND')}")
print(f"DB_PORT: {env_vars.get('DB_PORT', 'NOT FOUND')}")
print("-" * 70)

if not env_vars.get('DB_USER'):
    print("\n❌ ERROR: DB_USER not found in .env file!")
    exit(1)

print("\n🔌 Attempting database connection...")

def get_connection():
    return mysql.connector.connect(
        host=env_vars.get("DB_HOST"),
        user=env_vars.get("DB_USER"),
        password=env_vars.get("DB_PASSWORD"),
        port=int(env_vars.get("DB_PORT", 3306)),
        database=env_vars.get("DB_NAME", "bi_assetplan")
    )

def inspect():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        print("✅ Connected to database successfully!\n")
        
        print("="* 70)
        print("SEARCHING FOR RELEVANT TABLES")
        print("=" * 70)
        
        print("\n--- TABLES LIKE '%unidades%' ---")
        cursor.execute("SHOW TABLES LIKE '%unidades%'")
        unidades_tables = cursor.fetchall()
        if unidades_tables:
            for x in unidades_tables: print(f"  ✓ {x[0]}")
        else:
            print("  (none found)")
        
        print("\n--- TABLES LIKE '%stock%' ---")
        cursor.execute("SHOW TABLES LIKE '%stock%'")
        stock_tables = cursor.fetchall()
        if stock_tables:
            for x in stock_tables: print(f"  ✓ {x[0]}")
        else:
            print("  (none found)")

        
        print("\n--- TABLES LIKE '%contrato%' ---")
        cursor.execute("SHOW TABLES LIKE '%contrato%'")
        contrato_tables = cursor.fetchall()
        if contrato_tables:
            for x in contrato_tables: print(f"  ✓ {x[0]}")
        else:
            print("  (none found)")
        
        print("\n--- TABLES LIKE '%propiedad%' ---")
        cursor.execute("SHOW TABLES LIKE '%propiedad%'")
        propiedad_tables = cursor.fetchall()
        if propiedad_tables:
            for x in propiedad_tables: print(f"  ✓ {x[0]}")
        else:
            print("  (none found)")

        print("\n--- TABLES LIKE '%lead%' ---")
        cursor.execute("SHOW TABLES LIKE '%lead%'")
        lead_tables = cursor.fetchall()
        if lead_tables:
            for x in lead_tables: print(f"  ✓ {x[0]}")
        else:
            print("  (none found)")

        print("\n\n" + "=" * 70)
        print("ALL TABLES (first 30)")
        print("=" * 70)
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for i, table in enumerate(tables[:30]):
            print(f"{i+1:2}. {table[0]}")
        print(f"\n   (Total: {len(tables)} tables in database)")

        # Check 'leads' table structure
        if lead_tables:
            lead_table_name = lead_tables[0][0]
            print("\n\n" + "=" * 70)
            print(f"STRUCTURE OF '{lead_table_name}' TABLE")
            print("=" * 70)
            try:
                cursor.execute(f"DESCRIBE {lead_table_name}")
                cols = cursor.fetchall()
                for col in cols:
                    print(f"  {col[0]:25} | {col[1]}")
            except Exception as e:
                print(f"  Error: {e}")

    except Exception as e:
        print(f"\n❌ Database Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("\n\n🔌 Connection closed.")

if __name__ == "__main__":
    inspect()
