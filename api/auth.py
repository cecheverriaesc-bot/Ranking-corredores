#!/usr/bin/env python3
"""
API Endpoint: Autenticación Segura
Reemplaza la contraseña hardcodeada con autenticación real.
"""

from http.server import BaseHTTPRequestHandler
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse
import json

# ===================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ===================================================================

# Usar variables de entorno para secrets
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_hex(32))
TOKEN_EXPIRY_HOURS = 24

# Rate limiting storage
login_attempts = {}

# ===================================================================
# FUNCIONES DE SEGURIDAD
# ===================================================================

def hash_password(password: str, salt: str = None) -> tuple:
    """Genera hash seguro de contraseña usando PBKDF2"""
    if salt is None:
        salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # Iteraciones
    )
    return password_hash.hex(), salt

def generate_token(email: str, role: str) -> str:
    """Genera token seguro con expiración"""
    token = secrets.token_urlsafe(32)
    return token

def check_rate_limit(ip: str, max_attempts: int = 5, window_minutes: int = 5) -> bool:
    """
    Verifica rate limiting para login.
    Retorna True si está permitido, False si excedió el límite.
    """
    now = datetime.now()
    window = timedelta(minutes=window_minutes)
    
    if ip not in login_attempts:
        login_attempts[ip] = []
    
    # Limpiar intentos viejos
    login_attempts[ip] = [
        t for t in login_attempts[ip]
        if now - t < window
    ]
    
    if len(login_attempts[ip]) >= max_attempts:
        return False
    
    login_attempts[ip].append(now)
    return True

def cleanup_old_attempts():
    """Limpia intentos de login viejos"""
    now = datetime.now()
    for ip in list(login_attempts.keys()):
        login_attempts[ip] = [
            t for t in login_attempts[ip]
            if now - t < timedelta(hours=1)
        ]
        if not login_attempts[ip]:
            del login_attempts[ip]

# ===================================================================
# GESTIÓN DE TOKENS (En producción, usar Redis o DB)
# ===================================================================

active_tokens = {}

def store_token(token: str, email: str, role: str, squad: str = None):
    """Almacena token activo"""
    active_tokens[token] = {
        'email': email,
        'role': role,
        'squad': squad or email,
        'expires': datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    }

def validate_token(token: str) -> dict | None:
    """Valida token y retorna información del usuario"""
    if token not in active_tokens:
        return None
    
    token_data = active_tokens[token]
    if datetime.now() > token_data['expires']:
        del active_tokens[token]
        return None
    
    return token_data

def revoke_token(token: str):
    """Revoca un token"""
    if token in active_tokens:
        del active_tokens[token]

# ===================================================================
# USUARIOS AUTORIZADOS
# En producción, esto debería venir de una base de datos
# ===================================================================

AUTHORIZED_USERS = {
    'carlos.echeverria@assetplan.cl': {
        'password_hash': None,
        'salt': None,
        'role': 'admin',
        'squad': 'carlos.echeverria@assetplan.cl',
        'name': 'Carlos Echeverria'
    },
    'luis.gomez@assetplan.cl': {
        'password_hash': None,
        'salt': None,
        'role': 'coordinator',
        'squad': 'luis.gomez@assetplan.cl',
        'name': 'Luis Gomez'
    },
    'nataly.venegas@assetplan.cl': {
        'password_hash': None,
        'salt': None,
        'role': 'coordinator',
        'squad': 'nataly.venegas@assetplan.cl',
        'name': 'Nataly Venegas'
    },
    'angely.perez@assetplan.cl': {
        'password_hash': None,
        'salt': None,
        'role': 'coordinator',
        'squad': 'angely.perez@assetplan.cl',
        'name': 'Angely Perez'
    }
}

# ===================================================================
# HTTP REQUEST HANDLER
# ===================================================================

class handler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """Logging personalizado"""
        print(f"[AUTH API] {self.client_address[0]} - {format % args}")
    
    def do_POST(self):
        """
        POST /api/auth/login
        Body: {"email": "user@assetplan.cl", "password": "secure_password"}
        """
        # Rate limiting
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip, max_attempts=5, window_minutes=5):
            self.send_response(429)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Retry-After', '300')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Demasiados intentos. Intente en 5 minutos.'
            }).encode())
            return
        
        # Parsear body
        content_length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(content_length).decode('utf-8'))
            email = body.get('email', '').lower().strip()
            password = body.get('password', '')
        except:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'JSON inválido'
            }).encode())
            return
        
        # Validaciones básicas
        if not email or not password:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Email y contraseña son requeridos'
            }).encode())
            return
        
        # Verificar dominio de email
        valid_domains = ['@assetplan.cl', '@arriendos-assetplan.cl']
        if not any(domain in email for domain in valid_domains):
            self.send_response(403)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Debe usar email corporativo (@assetplan.cl o @arriendos-assetplan.cl)'
            }).encode())
            return
        
        # Verificar usuario autorizado
        if email not in AUTHORIZED_USERS:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Usuario no autorizado'
            }).encode())
            return
        
        user = AUTHORIZED_USERS[email]
        
        # Primer login - establecer contraseña (solo para desarrollo)
        # En producción, las contraseñas deben estar pre-configuradas
        if user['password_hash'] is None:
            # NOTA: En producción, esto debe hacerse mediante admin panel
            password_hash, salt = hash_password(password)
            user['password_hash'] = password_hash
            user['salt'] = salt
            print(f"[AUTH] Contraseña inicial establecida para {email}")
        
        # Verificar contraseña
        password_hash, _ = hash_password(password, user['salt'])
        if password_hash != user['password_hash']:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Contraseña incorrecta'
            }).encode())
            return
        
        # Generar token
        token = generate_token(email, user['role'])
        store_token(token, email, user['role'], user.get('squad'))
        
        # Respuesta exitosa
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': True,
            'token': token,
            'user': {
                'email': email,
                'role': user['role'],
                'squad': user.get('squad'),
                'name': user.get('name', email.split('@')[0])
            },
            'expires_in': TOKEN_EXPIRY_HOURS * 3600
        }).encode())
    
    def do_GET(self):
        """
        GET /api/auth/verify - Verificar token
        GET /api/auth/logout - Cerrar sesión
        """
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.endswith('/verify'):
            # Obtener token de headers
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'valid': False,
                    'error': 'Token requerido'
                }).encode())
                return
            
            token = auth_header[7:]  # Remover "Bearer "
            token_data = validate_token(token)
            
            if token_data:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'valid': True,
                    'user': token_data
                }).encode())
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'valid': False,
                    'error': 'Token inválido o expirado'
                }).encode())
        
        elif parsed_path.path.endswith('/logout'):
            # Logout
            auth_header = self.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                revoke_token(token)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'Sesión cerrada'
            }).encode())
        
        elif parsed_path.path.endswith('/users'):
            """GET /api/auth/users - Lista de usuarios autorizados (solo para admin)"""
            # Verificar admin
            auth_header = self.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                token_data = validate_token(token)
                
                if not token_data or token_data.get('role') != 'admin':
                    self.send_response(403)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'Acceso denegado'
                    }).encode())
                    return
            
            # Retornar lista sin información sensible
            users_list = [
                {'email': email, 'role': data['role'], 'name': data.get('name')}
                for email, data in AUTHORIZED_USERS.items()
            ]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(users_list).encode())
    
    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
