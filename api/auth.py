#!/usr/bin/env python3
"""
API Endpoint: Autenticación Segura (Stateless para Vercel)
Implementa validación de tokens por HMAC. No almacena estado en memoria.
"""

from http.server import BaseHTTPRequestHandler
import hashlib
import hmac
import os
import json
import base64
from datetime import datetime, timedelta
from urllib.parse import urlparse

# ===================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ===================================================================
# Se requiere un secreto fijo para que firmas coincidan entre instancias.
# Si no hay env configurada en Vercel, se usa un default seguro provisorio.
JWT_SECRET = os.environ.get('JWT_SECRET', 'AssetplanRankingSecret2026_SecureKey_v1')
TOKEN_EXPIRY_HOURS = 24
# Contraseña general para coordinadores y accesos administrativos.
MASTER_PASSWORD = os.environ.get('MASTER_PASSWORD', 'Assetplan2026')

# ===================================================================
# FUNCIONES DE SEGURIDAD STATELESS (Tokens)
# ===================================================================

def generate_stateless_token(email: str, role: str, squad: str) -> str:
    """Genera un token firmado HMAC. payload = email|role|squad|expires"""
    expires = int((datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)).timestamp())
    payload = f"{email}|{role}|{squad}|{expires}"
    
    # Firmar el payload
    signature = hmac.new(
        JWT_SECRET.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    encoded_signature = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    encoded_payload = base64.urlsafe_b64encode(payload.encode('utf-8')).decode('utf-8').rstrip('=')
    
    return f"{encoded_payload}.{encoded_signature}"

def validate_stateless_token(token: str) -> dict | None:
    """Valida la firma HMAC y expiración. Retorna dict user data o None."""
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return None
        
        encoded_payload, encoded_signature = parts
        
        # Validar payload
        # Pad strings for base64 decoding (add '=' until length is multiple of 4)
        padded_payload = encoded_payload + '=' * (-len(encoded_payload) % 4)
        padded_sig = encoded_signature + '=' * (-len(encoded_signature) % 4)
        
        payload = base64.urlsafe_b64decode(padded_payload).decode('utf-8')
        signature_provided = base64.urlsafe_b64decode(padded_sig)
        
        # Recrear firma
        expected_signature = hmac.new(
            JWT_SECRET.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        if not hmac.compare_digest(expected_signature, signature_provided):
            return None
            
        # Validar contenido y expiración
        email, role, squad, expires_str = payload.split('|')
        
        if int(expires_str) < datetime.now().timestamp():
            return None # Expirado
            
        return {
            'email': email,
            'role': role,
            'squad': squad,
            'name': AUTHORIZED_USERS.get(email, {}).get('name', email.split('@')[0])
        }
    except Exception as e:
        print(f"[AUTH ERROR] Token validation err: {e}")
        return None

# ===================================================================
# USUARIOS AUTORIZADOS
# ===================================================================
AUTHORIZED_USERS = {
    'carlos.echeverria@assetplan.cl': {
        'role': 'admin',
        'squad': 'carlos.echeverria@assetplan.cl',
        'name': 'Carlos Echeverria'
    },
    'luis.gomez@assetplan.cl': {
        'role': 'coordinator',
        'squad': 'luis.gomez@assetplan.cl',
        'name': 'Luis Gomez'
    },
    'nataly.venegas@assetplan.cl': {
        'role': 'coordinator',
        'squad': 'nataly.venegas@assetplan.cl',
        'name': 'Nataly Venegas'
    },
    'angely.perez@assetplan.cl': {
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
                'error': 'Usuario no autorizado en el sistema de Ranking.'
            }).encode())
            return
        
        user = AUTHORIZED_USERS[email]
        
        # Validación de Master Password para ambiente Vercel
        if password != MASTER_PASSWORD:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Contraseña incorrecta'
            }).encode())
            return
        
        # Generar token Stateless
        token = generate_stateless_token(email, user['role'], user.get('squad', email))
        
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
                'squad': user.get('squad', email),
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
            token_data = validate_stateless_token(token)
            
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
            # El logout en modelo Stateless puro normalmente se maneja solo quitando el token 
            # desde el cliente (localStorage), ya que no guardamos el estado activo en servidor.
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'Sesión cerrada exitosamente en cliente.'
            }).encode())
        
        elif parsed_path.path.endswith('/users'):
            """GET /api/auth/users - Lista de usuarios autorizados (solo para admin)"""
            auth_header = self.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                token_data = validate_stateless_token(token)
                
                if not token_data or token_data.get('role') != 'admin':
                    self.send_response(403)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'Acceso denegado'
                    }).encode())
                    return
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No autorizado'}).encode())
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

