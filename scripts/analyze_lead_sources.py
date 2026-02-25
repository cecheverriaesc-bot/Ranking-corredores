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
        database="bi_assetplan"
    )

def analyze_lead_sources():
    """
    Deep dive into lead sources: what sources exist, volumes, conversion rates
    """
    output_path = r"c:\Users\assetplan\Desktop\Ranking Enero 2026\lead_source_analysis.json"
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    results = {}
    
    try:
        print("=" * 80)
        print("LEAD SOURCE INTELLIGENCE ANALYSIS")
        print("=" * 80)
        
        # 1. All unique lead sources
        print("\n1. Discovering all lead sources...")
        cursor.execute("""
            SELECT 
                fuente,
                COUNT(*) as total_leads,
                COUNT(DISTINCT lead_id) as unique_leads,
                MIN(created_at) as first_appearance,
                MAX(created_at) as last_appearance
            FROM bi_DimLeadAttemps
            WHERE YEAR(created_at) >= 2024
            GROUP BY fuente
            ORDER BY total_leads DESC
        """)
        
        sources = cursor.fetchall()
        results['sources_overview'] = sources
        print(f"   Found {len(sources)} different lead sources")
        for source in sources[:10]:
            print(f"   - {source['fuente']}: {source['total_leads']:,} leads")
        
        # 2. Lead sources by month (trend)
        print("\n2. Analyzing source trends (2024-2026)...")
        cursor.execute("""
            SELECT 
                fuente,
                DATE_FORMAT(created_at, '%Y-%m') as month,
                COUNT(DISTINCT lead_id) as leads_count
            FROM bi_DimLeadAttemps
            WHERE created_at >= '2024-01-01'
            GROUP BY fuente, month
            ORDER BY month DESC, leads_count DESC
        """)
        
        trends = cursor.fetchall()
        results['source_trends'] = trends
        print(f"   Tracked {len(trends)} source-month combinations")
        
        # 3. Source by comuna (geographic distribution)
        print("\n3. Analyzing geographic distribution by source...")
        cursor.execute("""
            SELECT 
                fuente,
                comuna,
                COUNT(DISTINCT lead_id) as leads_count,
                COUNT(DISTINCT property_id) as properties_count
            FROM bi_DimLeadAttemps
            WHERE YEAR(created_at) = 2026
            GROUP BY fuente, comuna
            HAVING leads_count > 5
            ORDER BY fuente, leads_count DESC
        """)
        
        geo_dist = cursor.fetchall()
        results['geographic_distribution'] = geo_dist
        print(f"   Analyzed {len(geo_dist)} source-comuna combinations")
        
        # 4. Conversion by source (Lead -> Cotización)
        print("\n4. Calculating conversion rates by source (Lead -> Quote)...")
        cursor.execute("""
            SELECT 
                la.fuente,
                COUNT(DISTINCT la.lead_id) as total_leads,
                COUNT(DISTINCT cot.lead_id) as leads_with_quote,
                ROUND(COUNT(DISTINCT cot.lead_id) / COUNT(DISTINCT la.lead_id) * 100, 2) as conversion_to_quote_pct
            FROM bi_DimLeadAttemps la
            LEFT JOIN bi_DimCotizaciones cot ON la.lead_id = cot.lead_id
            WHERE YEAR(la.created_at) = 2026
            GROUP BY la.fuente
            HAVING total_leads > 10
            ORDER BY conversion_to_quote_pct DESC
        """)
        
        conversions = cursor.fetchall()
        results['source_conversions'] = conversions
        print(f"   Calculated conversion for {len(conversions)} sources")
        for conv in conversions[:5]:
            print(f"   - {conv['fuente']}: {conv['conversion_to_quote_pct']}% conversion")
        
        # 5. Subtipología preferences by source
        print("\n5. Analyzing property type preferences by source...")
        cursor.execute("""
            SELECT 
                fuente,
                subtipologia,
                COUNT(*) as preferences_count
            FROM bi_DimLeadAttemps
            WHERE YEAR(created_at) = 2026
              AND subtipologia IS NOT NULL
            GROUP BY fuente, subtipologia
            ORDER BY fuente, preferences_count DESC
        """)
        
        preferences = cursor.fetchall()
        results['type_preferences'] = preferences
        print(f"   Analyzed {len(preferences)} source-type combinations")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✅ Analysis complete! Results saved to: {output_path}")
        print(f"\nSummary:")
        print(f"  - Total Sources: {len(sources)}")
        print(f"  - Time Series Data Points: {len(trends)}")
        print(f"  - Geographic Combinations: {len(geo_dist)}")
        print(f"  - Conversion Rates Calculated: {len(conversions)}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()
        print("\n🔌 Connection closed.")

if __name__ == "__main__":
    analyze_lead_sources()
