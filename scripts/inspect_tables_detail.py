
import mysql.connector
import os

print("=" * 70)
print("DETAILED TABLE STRUCTURE INSPECTOR")
print("=" * 70)

# Manual .env loading
env_vars = {}
env_file_path = r"c:\Users\assetplan\Desktop\Ranking Enero 2026\Gobernanza_Ranking_2026\.env"

if os.path.exists(env_file_path):
    with open(env_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

def get_connection():
    return mysql.connector.connect(
        host=env_vars.get("DB_HOST"),
        user=env_vars.get("DB_USER"),
        password=env_vars.get("DB_PASSWORD"),
        port=int(env_vars.get("DB_PORT", 3306)),
        database=env_vars.get("DB_NAME", "bi_assetplan")
    )

def inspect_table(cursor, table_name):
    print(f"\n{'=' * 70}")
    print(f"TABLE: {table_name}")
    print("=" * 70)
    try:
        cursor.execute(f"DESCRIBE {table_name}")
        cols = cursor.fetchall()
        print(f"{'Column':<30} | {'Type':<25} | Null | Key")
        print("-" * 70)
        for col in cols:
            print(f"{col[0]:<30} | {col[1]:<25} | {col[2]:<4} | {col[3]}")
        
        # Sample data
        print(f"\n{'Sample Data (first 3 rows):'}")
        print("-" * 70)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"  {row[:5]}...")  # Show first 5 columns only
        else:
            print("  (no data)")
            
    except Exception as e:
        print(f"  Error: {e}")

def main():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        print("✅ Connected to database\n")
        
        # Tables of interest for the Laboratory
        tables_to_inspect = [
            'bi_DimContratos',        # Contracts
            'bi_DimLeadAttemps',      # Leads
            'bi_DimAgendas',          # Appointments/Visits
            'bi_DimCorredores',       # Brokers
            'bi_DimCotizaciones'      # Quotes (might have comuna/location)
        ]
        
        for table in tables_to_inspect:
            inspect_table(cursor, table)
        
        # Search for property/unit tables
        print(f"\n\n{'=' * 70}")
        print("SEARCHING FOR PROPERTY/UNIT TABLES")
        print("=" * 70)
        
        # Try each pattern separately
        patterns = ['%property%', '%unidad%', '%propiedad%']
        found_tables = set()
        for pattern in patterns:
            cursor.execute(f"SHOW TABLES LIKE '{pattern}'")
            for table in cursor.fetchall():
                found_tables.add(table[0])
        
        if found_tables:
            for table in found_tables:
                inspect_table(cursor, table)
        else:
            print("(no property tables found with standard names)")

            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("\n\n🔌 Connection closed.")

if __name__ == "__main__":
    main()
