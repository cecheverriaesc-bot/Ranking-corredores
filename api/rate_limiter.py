#!/usr/bin/env python3
"""
Middleware de Rate Limiting para APIs
Protege contra brute force y abuso de APIs.
"""

from datetime import datetime, timedelta
import json

# ===================================================================
# ALMACENAMIENTO DE REQUESTS (En producción, usar Redis)
# ===================================================================

class RateLimiter:
    """
    Rate limiter simple usando diccionario en memoria.
    Para producción, usar Redis con TTL automático.
    """
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, identifier: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """
        Verifica si el identificador puede hacer request.
        
        Args:
            identifier: Identificador único (IP, email, token)
            max_requests: Máximo de requests permitidos en la ventana
            window_seconds: Ventana de tiempo en segundos
        
        Returns:
            True si está permitido, False si excedió el límite
        """
        now = datetime.now()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Limpiar timestamps viejos
        self.requests[identifier] = [
            ts for ts in self.requests[identifier]
            if (now - ts).total_seconds() < window_seconds
        ]
        
        # Verificar límite
        if len(self.requests[identifier]) >= max_requests:
            return False
        
        # Registrar request
        self.requests[identifier].append(now)
        return True
    
    def get_remaining(self, identifier: str, max_requests: int = 10, window_seconds: int = 60) -> int:
        """Retorna cuántos requests restantes tiene el identificador"""
        now = datetime.now()
        
        if identifier not in self.requests:
            return max_requests
        
        valid_requests = [
            ts for ts in self.requests[identifier]
            if (now - ts).total_seconds() < window_seconds
        ]
        
        return max(0, max_requests - len(valid_requests))
    
    def cleanup(self):
        """Limpia identificadores expirados"""
        now = datetime.now()
        expired = []
        
        for identifier, timestamps in self.requests.items():
            valid = [
                ts for ts in timestamps
                if (now - ts).total_seconds() < 3600
            ]
            if valid:
                self.requests[identifier] = valid
            else:
                expired.append(identifier)
        
        for identifier in expired:
            del self.requests[identifier]

# Instancia global
rate_limiter = RateLimiter()

# ===================================================================
# CONFIGURACIÓN DE RATE LIMITS POR ENDPOINT
# ===================================================================

class APIRateLimits:
    """Configuración de rate limits por tipo de endpoint"""
    
    LOGIN = {'max_requests': 5, 'window_seconds': 300}  # 5 intentos cada 5 min
    DATA_API = {'max_requests': 30, 'window_seconds': 60}  # 30 requests por min
    WRITE_API = {'max_requests': 10, 'window_seconds': 60}  # 10 writes por min
    PUBLIC_API = {'max_requests': 100, 'window_seconds': 60}  # 100 requests por min

# ===================================================================
# FUNCIONES HELPER PARA HANDLERS
# ===================================================================

def check_rate_limit(handler, rate_config: dict = None) -> bool:
    """
    Verifica rate limit para un handler.
    Retorna True si está permitido, False si excedió.
    """
    if rate_config is None:
        rate_config = APIRateLimits.DATA_API
    
    client_ip = handler.client_address[0]
    
    if not rate_limiter.is_allowed(
        client_ip,
        max_requests=rate_config['max_requests'],
        window_seconds=rate_config['window_seconds']
    ):
        send_rate_limit_response(handler, rate_config['window_seconds'])
        return False
    
    return True

def send_rate_limit_response(handler, retry_after: int = 60):
    """Envía respuesta 429 Too Many Requests"""
    handler.send_response(429)
    handler.send_header('Content-type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Retry-After', str(retry_after))
    handler.end_headers()
    
    error_response = {
        'success': False,
        'error': 'Too Many Requests',
        'message': 'Has excedido el límite de requests. Intente más tarde.',
        'retry_after': retry_after
    }
    handler.wfile.write(json.dumps(error_response).encode())

# ===================================================================
# DECORADORES PARA VALIDACIÓN DE INPUT
# ===================================================================

def validate_query_params(params: dict, validators: dict) -> tuple:
    """
    Valida parámetros de query string.
    
    Args:
        params: Diccionario de parámetros
        validators: Diccionario de validadores {'param': (type, min, max, required)}
    
    Returns:
        (validated_data, error_message)
    """
    validated = {}
    
    for param, (param_type, min_val, max_val, required) in validators.items():
        value = params.get(param, [None])[0]
        
        if value is None:
            if required:
                return None, f"Parámetro requerido: {param}"
            continue
        
        try:
            if param_type == int:
                value = int(value)
            elif param_type == float:
                value = float(value)
            elif param_type == str:
                value = str(value)
            
            if min_val is not None and value < min_val:
                return None, f"{param} debe ser >= {min_val}"
            
            if max_val is not None and value > max_val:
                return None, f"{param} debe ser <= {max_val}"
            
            validated[param] = value
            
        except (ValueError, TypeError):
            return None, f"{param} debe ser de tipo {param_type.__name__}"
    
    return validated, None

# ===================================================================
# CORS HELPER
# ===================================================================

ALLOWED_ORIGINS = [
    'https://ranking.assetplan.cl',
    'https://ranking-assetplan.vercel.app',
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173'
]

def get_cors_headers(origin: str = None) -> dict:
    """
    Retorna headers de CORS apropiados.
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    }
    
    if origin and origin in ALLOWED_ORIGINS:
        headers['Access-Control-Allow-Origin'] = origin
        headers['Access-Control-Allow-Credentials'] = 'true'
    
    return headers

def send_cors_headers(handler, origin: str = None):
    """Envía headers de CORS en un handler"""
    headers = get_cors_headers(origin)
    for key, value in headers.items():
        handler.send_header(key, value)

# ===================================================================
# CLASE BASE PARA HANDLERS
# ===================================================================

class BaseAPIHandler:
    """
    Clase base para handlers con rate limiting y CORS.
    
    Uso:
        class MyAPIHandler(BaseAPIHandler, BaseHTTPRequestHandler):
            def do_GET(self):
                if not self.check_rate_limit():
                    return
                # ... resto del código
    """
    
    rate_limit_config = APIRateLimits.DATA_API
    
    def get_client_ip(self) -> str:
        return self.client_address[0]
    
    def check_rate_limit(self, config: dict = None) -> bool:
        """Verifica rate limit"""
        if config is None:
            config = self.rate_limit_config
        return check_rate_limit(self, config)
    
    def send_json_response(self, data: dict, status: int = 200):
        """Envía respuesta JSON"""
        origin = self.headers.get('Origin', '')
        self.send_response(status)
        send_cors_headers(self, origin)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, message: str, status: int = 400):
        """Envía respuesta de error"""
        self.send_json_response({
            'success': False,
            'error': message
        }, status)
    
    def get_query_params(self) -> dict:
        """Obtiene parámetros de query string como dict simple"""
        from urllib.parse import parse_qs, urlparse
        parsed_path = urlparse(self.path)
        return parse_qs(parsed_path.query)
    
    def validate_params(self, validators: dict) -> tuple:
        """Valida parámetros de query"""
        params = self.get_query_params()
        return validate_query_params(params, validators)
