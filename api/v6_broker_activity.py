from http.server import BaseHTTPRequestHandler
import json
import mysql.connector
import os
from datetime import datetime, date, timedelta
import calendar
from urllib.parse import urlparse, parse_qs

# ===================================================================
# CARGA DE ENV VARS
# ===================================================================
def load_env_vars():
    env_file_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()

load_env_vars()

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        port=int(os.environ.get('DB_PORT', 3306)),
        database='bi_assetplan'
    )

# ===================================================================
# FETCH ACTIVIDAD SEMANAL REAL POR CORREDOR
# ===================================================================
def fetch_broker_activity(broker_name: str, weeks_back: int = 16):
    """
    Obtiene actividad semanal de un corredor en las últimas N semanas.
    
    Retorna:
    {
        "broker": "Nombre Corredor",
        "weeks": [
            {
                "week": "2026-W05",
                "date": "2026-01-27",
                "agenda": 8,       # agendas creadas
                "visitadas": 5,     # visitas realizadas
                "leads": 12,        # leads asignados
                "reservas": 2       # reservas generadas
            },
            ...
        ]
    }
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fecha inicio: N semanas atrás
        start_date = date.today() - timedelta(weeks=weeks_back)

        # ----------------------------------------------------------------
        # 1) ACTIVIDAD DE AGENDAS por semana
        # ----------------------------------------------------------------
        cursor.execute("""
            SELECT 
                YEARWEEK(a.created_at, 1) AS week_key,
                MIN(DATE(a.created_at)) AS week_start,
                COUNT(*) AS agenda_total,
                SUM(CASE WHEN a.estado = 'Visitado' THEN 1 ELSE 0 END) AS visitadas,
                SUM(CASE WHEN a.estado = 'Cancelado' THEN 1 ELSE 0 END) AS canceladas
            FROM bi_DimAgendas a
            JOIN bi_DimCorredores c ON a.corredor_id = c.corredor_id
            WHERE c.nombre_corredor = %s
              AND a.created_at >= %s
            GROUP BY YEARWEEK(a.created_at, 1)
            ORDER BY week_key
        """, (broker_name, start_date))
        agenda_rows = cursor.fetchall()

        # ----------------------------------------------------------------
        # 2) LEADS asignados por semana
        # ----------------------------------------------------------------
        cursor.execute("""
            SELECT 
                YEARWEEK(la.created_at, 1) AS week_key,
                COUNT(*) AS leads_total
            FROM bi_DimLeadAttemps la
            JOIN bi_DimCorredores c ON la.corredor_id = c.corredor_id
            WHERE c.nombre_corredor = %s
              AND la.created_at >= %s
            GROUP BY YEARWEEK(la.created_at, 1)
            ORDER BY week_key
        """, (broker_name, start_date))
        leads_rows = cursor.fetchall()
        leads_by_week = {r['week_key']: r['leads_total'] for r in leads_rows}

        # ----------------------------------------------------------------
        # 3) RESERVAS por semana (contratos tipo arriendo)
        # ----------------------------------------------------------------
        cursor.execute("""
            SELECT 
                YEARWEEK(co.created_at, 1) AS week_key,
                COUNT(*) AS reservas_total
            FROM bi_DimContratos co
            JOIN bi_DimCorredores c ON co.corredor_id = c.corredor_id
            WHERE c.nombre_corredor = %s
              AND co.created_at >= %s
            GROUP BY YEARWEEK(co.created_at, 1)
            ORDER BY week_key
        """, (broker_name, start_date))
        reservas_rows = cursor.fetchall()
        reservas_by_week = {r['week_key']: r['reservas_total'] for r in reservas_rows}

        # ----------------------------------------------------------------
        # 4) Unificar semanas: semanas con al menos agenda ó leads
        # ----------------------------------------------------------------
        all_week_keys = sorted(set(
            [r['week_key'] for r in agenda_rows] +
            list(leads_by_week.keys()) +
            list(reservas_by_week.keys())
        ))

        agenda_by_week = {
            r['week_key']: r for r in agenda_rows
        }

        weeks_output = []
        for wk in all_week_keys:
            ag = agenda_by_week.get(wk, {})
            week_start = ag.get('week_start') or _week_start_from_yearweek(wk)
            year = wk // 100
            week_num = wk % 100
            weeks_output.append({
                "week": f"{year}-W{week_num:02d}",
                "date": str(week_start),
                "agenda": int(ag.get('agenda_total', 0)),
                "visitadas": int(ag.get('visitadas', 0)),
                "canceladas": int(ag.get('canceladas', 0)),
                "leads": int(leads_by_week.get(wk, 0)),
                "reservas": int(reservas_by_week.get(wk, 0))
            })

        return {
            "broker": broker_name,
            "weeks": weeks_output,
            "weeks_queried": weeks_back,
            "data_from": str(start_date)
        }

    except Exception as e:
        raise RuntimeError(f"Error fetching broker activity: {str(e)}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _week_start_from_yearweek(yearweek_int: int) -> date:
    """Convierte un YEARWEEK(x, 1) int en la fecha de inicio de la semana (lunes)."""
    year = yearweek_int // 100
    week = yearweek_int % 100
    # ISO: la semana 1 es la que contiene el primer jueves de enero
    try:
        return datetime.strptime(f"{year} {week} 1", "%G %V %u").date()
    except Exception:
        return date(year, 1, 1)


# ===================================================================
# HTTP HANDLER
# ===================================================================
class handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Silenciar logs de acceso en producción

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)

            broker_name = params.get('broker_name', [''])[0].strip()
            weeks_back = int(params.get('weeks_back', ['16'])[0])

            if not broker_name:
                self._send_json(400, {"error": "Parámetro 'broker_name' es requerido"})
                return

            data = fetch_broker_activity(broker_name, weeks_back)

            self._send_json(200, data)

        except RuntimeError as e:
            self._send_json(500, {"error": str(e)})
        except Exception as e:
            self._send_json(500, {"error": f"Error interno: {str(e)}"})

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload, default=str, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)
