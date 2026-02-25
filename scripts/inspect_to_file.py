
import mysql.connector
import os
import json

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

def inspect_table(conn, cursor, table_name, output_file):
    output_file.write(f"\n\n{'=' * 80}\n")
    output_file.write(f"TABLE: {table_name}\n")
    output_file.write("=" * 80 + "\n")
    try:
        # Get columns
        cursor.execute(f"DESCRIBE {table_name}")
        cols = cursor.fetchall()
        output_file.write(f"\n{'Column':<35} | {'Type':<30} | Null | Key\n")
        output_file.write("-" * 80 + "\n")
        for col in cols:
            output_file.write(f"{col[0]:<35} | {col[1]:<30} | {col[2]:<4} | {col[3]}\n")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchall()[0][0]
        output_file.write(f"\nTotal Rows: {count:,}\n")
        
        # Sample data (first 2 rows, showing all columns)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
        rows = cursor.fetchall()
        if rows:
            output_file.write(f"\nSample Data (first 2 rows):\n")
            output_file.write("-" * 80 + "\n")
            for i, row in enumerate(rows):
                output_file.write(f"Row {i+1}:\n")
                for j, val in enumerate(row[:10]):  # First 10 columns
                    col_name = cols[j][0] if j < len(cols) else f"col_{j}"
                    output_file.write(f"  {col_name}: {val}\n")
                if len(row) > 10:
                    output_file.write(f"  ... ({len(row) - 10} more columns)\n")
                output_file.write("\n")
        else:
            output_file.write("\n(No data in table)\n")
            
    except Exception as e:
        output_file.write(f"Error: {e}\n")

def main():
    output_path = r"c:\Users\assetplan\Desktop\Ranking Enero 2026\database_schema_report.txt"
    
    with open(output_path, 'w', encoding='utf-8') as output:
        output.write("=" * 80 + "\n")
        output.write("DATABASE SCHEMA INSPECTION REPORT\n")
        output.write("Database: bi_assetplan (Business Intelligence)\n")
        output.write("=" * 80 + "\n")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            output.write("\n✅ Connected to database successfully\n")
            
            # Tables of interest for the Laboratory
            tables = [
                'bi_DimContratos',
                'bi_DimLeadAttemps',
                'bi_DimAgendas',
                'bi_DimCorredores',
                'bi_DimCotizaciones'
            ]
            
            for table in tables:
                inspect_table(conn, cursor, table, output)
            
            output.write("\n\n" + "=" * 80 + "\n")
            output.write("INSPECTION COMPLETE\n")
            output.write("=" * 80 + "\n")
            
        except Exception as e:
            output.write(f"\n❌ Error: {e}\n")
            import traceback
            output.write(traceback.format_exc())
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()
                output.write("\n🔌 Database connection closed.\n")
    
    print(f"✅ Report written to: {output_path}")

if __name__ == "__main__":
    main()
