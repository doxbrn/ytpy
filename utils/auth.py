import jwt
import datetime
from functools import wraps
from typing import Optional, Dict, Any
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

class Auth:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self._blacklisted_tokens = set()

    def generate_token(self, user_id: str, expires_in: int = 3600) -> str:
        """
        Gera um token JWT
        
        Args:
            user_id: ID do usuário
            expires_in: Tempo de expiração em segundos
            
        Returns:
            Token JWT
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica um token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            Payload do token se válido, None caso contrário
        """
        if token in self._blacklisted_tokens:
            return None
            
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def blacklist_token(self, token: str) -> None:
        """
        Adiciona um token à blacklist
        
        Args:
            token: Token JWT para invalidar
        """
        self._blacklisted_tokens.add(token)

    def hash_password(self, password: str) -> str:
        """
        Gera hash de senha
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash da senha
        """
        return generate_password_hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verifica se uma senha corresponde ao hash
        
        Args:
            password: Senha em texto plano
            password_hash: Hash da senha
            
        Returns:
            True se a senha está correta
        """
        return check_password_hash(password_hash, password)

def require_auth(f):
    """
    Decorator para proteger rotas com autenticação
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Token não fornecido'}), 401
            
        try:
            token = auth_header.split(" ")[1]
            auth = current_app.config['auth']
            payload = auth.verify_token(token)
            
            if not payload:
                return jsonify({'error': 'Token inválido'}), 401
                
            # Adiciona o user_id ao request
            request.user_id = payload['user_id']
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 401
            
    return decorated

def admin_required(f):
    """
    Decorator para proteger rotas que requerem privilégios de admin
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Token não fornecido'}), 401
            
        try:
            token = auth_header.split(" ")[1]
            auth = current_app.config['auth']
            payload = auth.verify_token(token)
            
            if not payload:
                return jsonify({'error': 'Token inválido'}), 401
                
            # Verifica se o usuário é admin
            if not payload.get('is_admin', False):
                return jsonify({'error': 'Acesso negado'}), 403
                
            request.user_id = payload['user_id']
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 401
            
    return decorated
