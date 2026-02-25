from http.server import BaseHTTPRequestHandler
import json
import os
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        results = {}
        
        # Test 1: Basic Python
        results["python_version"] = sys.version
        
        # Test 2: Environment variables
        results["db_host_exists"] = "DB_HOST" in os.environ
        results["db_user_exists"] = "DB_USER" in os.environ
        results["db_password_exists"] = "DB_PASSWORD" in os.environ
        
        # Test 3: Import statistics
        try:
            import statistics
            results["statistics_import"] = "OK"
        except Exception as e:
            results["statistics_import"] = str(e)
        
        # Test 4: Import math
        try:
            import math
            results["math_import"] = "OK"
        except Exception as e:
            results["math_import"] = str(e)
        
        # Test 5: Import mysql.connector
        try:
            import mysql.connector
            results["mysql_import"] = "OK"
        except Exception as e:
            results["mysql_import"] = str(e)
        
        # Test 6: DB Connection to bi_assetplan
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=os.environ.get('DB_HOST'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                port=int(os.environ.get('DB_PORT', 3306)),
                database='bi_assetplan'
            )
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.fetchone()
            cur.close()
            conn.close()
            results["db_connection"] = "OK"
        except Exception as e:
            results["db_connection"] = str(e)
        
        # Test 7: Try importing v2_intelligence
        try:
            from api.v2_intelligence import fetch_squad_intelligence
            results["v2_import"] = "OK"
        except Exception as e:
            results["v2_import"] = str(e)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(results, indent=2).encode())
