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

def analyze_broker_mobility():
    """
    Analiza los traslados/desplazamientos de corredores entre comunas
    para detectar ineficiencias y oportunidades de optimización geográfica
    """
    output_path = r"c:\Users\assetplan\Desktop\Ranking Enero 2026\broker_mobility_analysis.json"
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    results = {}
    
    try:
        print("=" * 80)
        print("BROKER MOBILITY & GEOGRAPHIC EFFICIENCY ANALYSIS")
        print("=" * 80)
        
        # 1. Comunas únicas visitadas por corredor
        print("\n1. Analyzing geographic coverage per broker...")
        cursor.execute("""
            SELECT 
                c.nombre_corredor,
                COUNT(DISTINCT la.comuna) as comunas_visited,
                COUNT(DISTINCT a.id) as total_agendas,
                GROUP_CONCAT(DISTINCT la.comuna ORDER BY la.comuna SEPARATOR ', ') as comuna_list
            FROM bi_DimCorredores c
            INNER JOIN bi_DimAgendas a ON c.corredor_id = a.corredor_id
            INNER JOIN bi_DimLeadAttemps la ON a.property_id = la.property_id
            WHERE c.coordinador = 'carlos.echeverria'
              AND c.activo = 1
              AND YEAR(a.created_at) = 2026
            GROUP BY c.nombre_corredor
            ORDER BY comunas_visited DESC
        """)
        
        coverage = cursor.fetchall()
        results['broker_coverage'] = coverage
        print(f"   Analyzed {len(coverage)} brokers")
        for broker in coverage[:5]:
            print(f"   - {broker['nombre_corredor']}: {broker['comunas_visited']} comunas, {broker['total_agendas']} visitas")
        
        # 2. Top comunas por corredor (concentración)
        print("\n2. Analyzing broker concentration by comuna...")
        cursor.execute("""
            SELECT 
                c.nombre_corredor,
                la.comuna,
                COUNT(DISTINCT a.id) as visits_count,
                ROUND(COUNT(DISTINCT a.id) / SUM(COUNT(DISTINCT a.id)) OVER (PARTITION BY c.nombre_corredor) * 100, 1) as concentration_pct
            FROM bi_DimCorredores c
            INNER JOIN bi_DimAgendas a ON c.corredor_id = a.corredor_id
            INNER JOIN bi_DimLeadAttemps la ON a.property_id = la.property_id
            WHERE c.coordinador = 'carlos.echeverria'
              AND c.activo = 1
              AND YEAR(a.created_at) = 2026
            GROUP BY c.nombre_corredor, la.comuna
            HAVING visits_count > 2
            ORDER BY c.nombre_corredor, visits_count DESC
        """)
        
        concentration = cursor.fetchall()
        results['broker_concentration'] = concentration
        print(f"   Found {len(concentration)} broker-comuna combinations")
        
        # 3. Dispersión geográfica (índice de fragmentación)
        print("\n3. Calculating geographic dispersion index...")
        cursor.execute("""
            SELECT 
                c.nombre_corredor,
                COUNT(DISTINCT la.comuna) as unique_comunas,
                COUNT(DISTINCT a.id) as total_visits,
                ROUND(COUNT(DISTINCT la.comuna) / COUNT(DISTINCT a.id), 3) as dispersion_index
            FROM bi_DimCorredores c
            INNER JOIN bi_DimAgendas a ON c.corredor_id = a.corredor_id
            INNER JOIN bi_DimLeadAttemps la ON a.property_id = la.property_id
            WHERE c.coordinador = 'carlos.echeverria'
              AND c.activo = 1
              AND YEAR(a.created_at) = 2026
            GROUP BY c.nombre_corredor
            HAVING total_visits > 5
            ORDER BY dispersion_index DESC
        """)
        
        dispersion = cursor.fetchall()
        results['geographic_dispersion'] = dispersion
        print(f"   Calculated dispersion for {len(dispersion)} brokers")
        print("\n   🚨 High dispersion (ineficiente, muchos traslados):")
        for broker in dispersion[:3]:
            print(f"      - {broker['nombre_corredor']}: {broker['dispersion_index']} (visits across {broker['unique_comunas']} comunas)")
        
        # 4. Patrones de movimiento por día de la semana
        print("\n4. Analyzing movement patterns by day of week...")
        cursor.execute("""
            SELECT 
                c.nombre_corredor,
                DAYNAME(a.created_at) as day_of_week,
                COUNT(DISTINCT la.comuna) as comunas_visited,
                COUNT(DISTINCT a.id) as visits
            FROM bi_DimCorredores c
            INNER JOIN bi_DimAgendas a ON c.corredor_id = a.corredor_id
            INNER JOIN bi_DimLeadAttemps la ON a.property_id = la.property_id
            WHERE c.coordinador = 'carlos.echeverria'
              AND c.activo = 1
              AND YEAR(a.created_at) = 2026
            GROUP BY c.nombre_corredor, day_of_week
            ORDER BY c.nombre_corredor, visits DESC
        """)
        
        day_patterns = cursor.fetchall()
        results['day_patterns'] = day_patterns
        print(f"   Analyzed {len(day_patterns)} broker-day combinations")
        
        # 5. Comunas con mayor fragmentación (muchos corredores, poca concentración)
        print("\n5. Identifying fragmented zones (many brokers, low concentration)...")
        cursor.execute("""
            SELECT 
                la.comuna,
                COUNT(DISTINCT c.corredor_id) as unique_brokers,
                COUNT(DISTINCT a.id) as total_visits,
                ROUND(COUNT(DISTINCT a.id) / COUNT(DISTINCT c.corredor_id), 1) as visits_per_broker
            FROM bi_DimLeadAttemps la
            INNER JOIN bi_DimAgendas a ON la.property_id = a.property_id
            INNER JOIN bi_DimCorredores c ON a.corredor_id = c.corredor_id
            WHERE c.coordinador = 'carlos.echeverria'
              AND c.activo = 1
              AND YEAR(a.created_at) = 2026
            GROUP BY la.comuna
            HAVING unique_brokers > 3
            ORDER BY visits_per_broker ASC
        """)
        
        fragmented_zones = cursor.fetchall()
        results['fragmented_zones'] = fragmented_zones
        print(f"   Found {len(fragmented_zones)} zones with fragmentation")
        print("\n   ⚠️  Most fragmented (opportunity to consolidate):")
        for zone in fragmented_zones[:5]:
            print(f"      - {zone['comuna']}: {zone['unique_brokers']} brokers, {zone['visits_per_broker']} visits/broker avg")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✅ Mobility analysis complete! Results saved to: {output_path}")
        print(f"\nKey Insights:")
        print(f"  - Brokers analyzed: {len(coverage)}")
        print(f"  - Average comunas per broker: {sum(b['comunas_visited'] for b in coverage) / len(coverage):.1f}")
        print(f"  - Fragmented zones: {len(fragmented_zones)}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()
        print("\n🔌 Connection closed.")

if __name__ == "__main__":
    analyze_broker_mobility()
