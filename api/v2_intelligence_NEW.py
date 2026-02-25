from flask import jsonify
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, date
import calendar

load_dotenv()

# ===================================================================
# CONSTANTES GLOBALES
# ===================================================================
META_GLOBAL_110 = 1707  # Meta total mensual (110%)
CURRENT_YEAR = 2026
CURRENT_MONTH = 1  # Enero

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=int(os.getenv('DB_PORT', 3306)),
        database='bi_assetplan'
    )

def calculate_dias_restantes():
    """Calcular días hábiles restantes del mes"""
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    dias_restantes = last_day - today.day
    # Ajustar por fines de semana si es necesario
    return max(dias_restantes, 1)

def fetch_squad_intelligence(coordinador_email):
    """
    Sistema de Inteligencia Completo con Metas Dinámicas
    - Data del mes actual (Enero 2026)
    - Metas basadas en participación histórica
    - Leads diarios necesarios
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # ==============================================================
        # PASO 1: Calcular participación histórica del equipo
        # ==============================================================
        cursor.execute('''
            SELECT SUM(reserva) as total_global 
            FROM bi_DimCorredores 
            WHERE activo = 1
        ''')
        total_global_hist = cursor.fetchone()['total_global'] or 1
        
        cursor.execute('''
            SELECT SUM(reserva) as total_equipo
            FROM bi_DimCorredores 
            WHERE coordinador = %s AND activo = 1
        ''', (coordinador_email,))
        total_equipo_hist = cursor.fetchone()['total_equipo'] or 0
        
        pct_equipo = total_equipo_hist / total_global_hist if total_global_hist > 0 else 0
        META_EQUIPO = int(META_GLOBAL_110 * pct_equipo)
        
        # ==============================================================
        # PASO 2: Contratos del equipo en el mes actual
        # ==============================================================
        cursor.execute('''
            SELECT COUNT(DISTINCT lead_id) as contratos_mes
            FROM bi_DimLeads
            WHERE YEAR(contrato_created_at) = %s 
              AND MONTH(contrato_created_at) = %s
              AND corredor_id IN (
                  SELECT corredor_id FROM bi_DimCorredores 
                  WHERE coordinador = %s AND activo = 1
              )
        ''', (CURRENT_YEAR, CURRENT_MONTH, coordinador_email))
        contratos_equipo_mes = cursor.fetchone()['contratos_mes'] or 0
        
        # ==============================================================
        # PASO 3: Data individual de corredores DEL MES
        # ==============================================================
        cursor.execute('''
            SELECT 
                c.corredor_id,
                c.nombre_corredor,
                c.reserva as reservas_historicas,
                COALESCE(l.contratos_mes, 0) as contratos_mes,
                COALESCE(l.leads_tomados_mes, 0) as leads_tomados_mes,
                COALESCE(l.prospectos_mes, 0) as prospectos_mes
            FROM bi_DimCorredores c
            LEFT JOIN (
                SELECT 
                    corredor_id,
                    COUNT(DISTINCT CASE WHEN contrato_created_at IS NOT NULL THEN lead_id END) as contratos_mes,
                    COUNT(DISTINCT lead_id) as leads_tomados_mes,
                    COUNT(DISTINCT CASE WHEN step_3_prospecto = 1 THEN lead_id END) as prospectos_mes
                FROM bi_DimLeads
                WHERE YEAR(fecha_tomado) = %s 
                  AND MONTH(fecha_tomado) = %s
                GROUP BY corredor_id
            ) l ON c.corredor_id = l.corredor_id
            WHERE c.coordinador = %s 
              AND c.activo = 1
            ORDER BY contratos_mes DESC, c.reserva DESC
        ''', (CURRENT_YEAR, CURRENT_MONTH, coordinador_email))
        
        corredores_data = cursor.fetchall()
        
        # ==============================================================
        # PASO 4: Métricas de visitas del mes
        # ==============================================================
        cursor.execute('''
            SELECT 
                corredor_id,
                COUNT(*) as total_agendas,
                SUM(CASE WHEN estado = 'Visitado' THEN 1 ELSE 0 END) as visitas_realizadas,
                SUM(CASE WHEN estado = 'Cancelado' THEN 1 ELSE 0 END) as visitas_canceladas
            FROM bi_DimAgendas
            WHERE YEAR(agenda_fecha) = %s 
              AND MONTH(agenda_fecha) = %s
              AND corredor_id IS NOT NULL
            GROUP BY corredor_id
        ''', (CURRENT_YEAR, CURRENT_MONTH))
        
        visit_metrics = {str(row['corredor_id']): row for row in cursor.fetchall()}
        
        # ==============================================================
        # PASO 5: Métricas de leads del mes
        # ==============================================================
        cursor.execute('''
            SELECT 
                corredor_id,
                COUNT(*) as total_leads,
                SUM(CASE WHEN lag_contacto IS NOT NULL AND lag_contacto <= 24 THEN 1 ELSE 0 END) as contacto_24h
            FROM bi_DimLeads
            WHERE YEAR(fecha_tomado) = %s 
              AND MONTH(fecha_tomado) = %s
              AND corredor_id IS NOT NULL
            GROUP BY corredor_id
        ''', (CURRENT_YEAR, CURRENT_MONTH))
        
        lead_metrics = {str(row['corredor_id']): row for row in cursor.fetchall()}
        
        # ==============================================================
        # PASO 6: Calcular metas individuales y scoring
        # ==============================================================
        dias_restantes = calculate_dias_restantes()
        brokers = []
        
        for corredor in corredores_data:
            corredor_id = str(corredor['corredor_id'])
            
            # Meta personalizada basada en participación histórica
            pct_corredor = corredor['reservas_historicas'] / total_equipo_hist if total_equipo_hist > 0 else 0
            meta_corredor = int(META_EQUIPO * pct_corredor)
            
            # Progreso y faltante
            contratos_mes = corredor['contratos_mes']
            faltante = max(meta_corredor - contratos_mes, 0)
            
            # Conversión del mes
            leads_mes = corredor['leads_tomados_mes']
            conv_mes = (corredor['prospectos_mes'] / leads_mes * 100) if leads_mes > 0 else 0
            
            # Leads necesarios
            if conv_mes > 0:
                leads_diarios_necesarios = int((faltante / dias_restantes) / (conv_mes / 100))
            else:
                leads_diarios_necesarios = 0
            
            # Visitas
            visit_data = visit_metrics.get(corredor_id, {})
            visitas_realizadas = visit_data.get('visitas_realizadas', 0)
            visitas_canceladas = visit_data.get('visitas_canceladas', 0)
            
            # Lead metrics
            lead_data = lead_metrics.get(corredor_id, {})
            contacto_24h = lead_data.get('contacto_24h', 0)
            total_leads_contacto = lead_data.get('total_leads', 1)
            
            # Scoring (simplificado por ahora)
            score = min(contratos_mes / max(meta_corredor, 1), 1.0) * 0.75
            
            if score >= 0.60:
                categoria = "Top Performer"
            elif score >= 0.40:categoria = "Promedio"
            else:
                categoria = "Coaching"
            
            # Acción recomendada
            if contratos_mes >= meta_corredor:
                action = "Meta Cumplida!"
            elif leads_diarios_necesarios > 0:
                action = f"Asignar {leads_diarios_necesarios} leads/día"
            else:
                action = "Revisar Conversión"
            
            brokers.append({
                "name": corredor['nombre_corredor'],
                "leads": leads_mes,
                "reservas": contratos_mes,
                "meta_personal": meta_corredor,
                "faltante": faltante,
                "conversion": f"{conv_mes:.1f}",
                "leadsNeeded": leads_diarios_necesarios,
                "action": action,
                "score": round(score, 3),
                "categoria": categoria,
                "visitas_realizadas": visitas_realizadas,
                "visitas_canceladas": visitas_canceladas
            })
        
        # ==============================================================
        # PASO 7: Métricas de Squad
        # ==============================================================
        total_leads_equipo = sum(b['leads'] for b in brokers)
        total_reservas_equipo = sum(b['reservas'] for b in brokers)
        conv_promedio_equipo = (total_reservas_equipo / total_leads_equipo * 100) if total_leads_equipo > 0 else 0
        
        squad_summary = {
            "total_brokers": len(brokers),
            "meta_equipo": META_EQUIPO,
            "contratos_actuales": contratos_equipo_mes,
            "faltante_equipo": max(META_EQUIPO - contratos_equipo_mes, 0),
            "conversion_promedio": f"{conv_promedio_equipo:.1f}%",
            "dias_restantes": dias_restantes
        }
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "brokers": brokers,
            "squad_summary": squad_summary,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500
