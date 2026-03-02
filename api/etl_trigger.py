#!/usr/bin/env python3
"""
API Endpoint: ETL Trigger
Ejecuta el script ETL para actualizar constants.ts con datos frescos.

Uso:
    POST /api/etl_trigger?secret=YOUR_SECRET
    
Variables de entorno requeridas:
    ETL_SECRET: Clave secreta para autorizar la ejecución
    ETL_ENABLED: "true" para habilitar ejecución remota (default: "false")
"""

from http.server import BaseHTTPRequestHandler
import subprocess
import os
import sys
import json
from urllib.parse import parse_qs, urlparse

# Añadir ruta para imports
sys.path.append(os.path.dirname(__file__))
from rate_limiter import check_rate_limit, APIRateLimits, send_cors_headers


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        POST /api/etl_trigger?secret=YOUR_SECRET
        Ejecuta el ETL para actualizar constants.ts
        """
        # Rate limiting estricto para este endpoint
        if not check_rate_limit(self, APIRateLimits.DATA_API):
            return
        
        # Verificar si ETL está habilitado
        etl_enabled = os.environ.get('ETL_ENABLED', 'false').lower()
        if etl_enabled != 'true':
            self.send_response(403)
            self.send_header('Content-type', 'application/json')
            send_cors_headers(self, self.headers.get('Origin', ''))
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'ETL remoto está deshabilitado',
                'message': 'Configure ETL_ENABLED=true para habilitar'
            }).encode())
            return
        
        # Verificar secret
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        secret = query_params.get('secret', [None])[0]
        
        expected_secret = os.environ.get('ETL_SECRET')
        if not expected_secret:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            send_cors_headers(self, self.headers.get('Origin', ''))
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'ETL_SECRET no configurado',
                'message': 'Configure la variable de entorno ETL_SECRET'
            }).encode())
            return
        
        if secret != expected_secret:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            send_cors_headers(self, self.headers.get('Origin', ''))
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Secret inválido',
                'authorized': False
            }).encode())
            return
        
        # Ejecutar ETL
        try:
            script_dir = os.path.dirname(__file__)
            etl_script = os.path.join(script_dir, '..', 'scripts', 'etl_ranking.py')
            
            if not os.path.exists(etl_script):
                raise FileNotFoundError(f"ETL script not found: {etl_script}")
            
            # Ejecutar script
            result = subprocess.run(
                ['python', etl_script],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            send_cors_headers(self, self.headers.get('Origin', ''))
            self.end_headers()
            
            response = {
                'status': 'success',
                'executed': True,
                'stdout': result.stdout[-1000:] if result.stdout else '',  # Últimos 1000 chars
                'stderr': result.stderr[-1000:] if result.stderr else '',
                'returncode': result.returncode
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except subprocess.TimeoutExpired:
            self.send_response(504)
            self.send_header('Content-type', 'application/json')
            send_cors_headers(self, self.headers.get('Origin', ''))
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Timeout',
                'message': 'ETL excedió el tiempo máximo de 5 minutos'
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            send_cors_headers(self, self.headers.get('Origin', ''))
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'ETL failed',
                'message': str(e)
            }).encode())
    
    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        send_cors_headers(self, self.headers.get('Origin', ''))
        self.end_headers()
    
    def do_GET(self):
        """
        GET /api/etl_trigger
        Retorna estado del ETL (no ejecuta)
        """
        etl_enabled = os.environ.get('ETL_ENABLED', 'false').lower()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        send_cors_headers(self, self.headers.get('Origin', ''))
        self.end_headers()
        
        self.wfile.write(json.dumps({
            'etl_enabled': etl_enabled == 'true',
            'etl_secret_configured': os.environ.get('ETL_SECRET') is not None,
            'endpoint': '/api/etl_trigger',
            'method': 'POST',
            'documentation': 'Send POST with ?secret=YOUR_SECRET to trigger ETL'
        }).encode())
