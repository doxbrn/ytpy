import time
from typing import Dict, Tuple
from collections import defaultdict
from threading import Lock
from functools import wraps
from flask import request, jsonify

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.lock = Lock()

    def _cleanup_old_requests(self, ip: str) -> None:
        """Remove requisições antigas"""
        current = time.time()
        with self.lock:
            self.requests[ip] = [
                req_time for req_time in self.requests[ip]
                if current - req_time < 60
            ]

    def is_allowed(self, ip: str) -> Tuple[bool, int]:
        """
        Verifica se uma requisição é permitida
        
        Args:
            ip: Endereço IP do cliente
            
        Returns:
            Tupla (permitido, tempo_espera)
        """
        self._cleanup_old_requests(ip)
        
        with self.lock:
            if len(self.requests[ip]) >= self.requests_per_minute:
                oldest_request = self.requests[ip][0]
                wait_time = int(60 - (time.time() - oldest_request))
                return False, wait_time
            
            self.requests[ip].append(time.time())
            return True, 0

def rate_limit(limiter: RateLimiter):
    """
    Decorator para aplicar rate limiting em rotas
    
    Args:
        limiter: Instância do RateLimiter
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            allowed, wait_time = limiter.is_allowed(ip)
            
            if not allowed:
                response = {
                    'error': 'Too many requests',
                    'wait_time': wait_time
                }
                return jsonify(response), 429
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class EndpointRateLimiter:
    """Rate limiter específico por endpoint"""
    
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {
            'default': RateLimiter(60),  # 60 req/min padrão
            'download': RateLimiter(10),  # 10 downloads/min
            'info': RateLimiter(30),     # 30 info requests/min
            'analytics': RateLimiter(20)  # 20 analytics requests/min
        }

    def get_limiter(self, endpoint: str) -> RateLimiter:
        """
        Obtém o rate limiter apropriado para um endpoint
        
        Args:
            endpoint: Nome do endpoint
            
        Returns:
            RateLimiter apropriado
        """
        # Identifica o tipo de endpoint
        if 'download' in endpoint:
            return self.limiters['download']
        elif 'info' in endpoint:
            return self.limiters['info']
        elif 'analytics' in endpoint:
            return self.limiters['analytics']
        return self.limiters['default']

def endpoint_rate_limit():
    """
    Decorator para aplicar rate limiting específico por endpoint
    """
    limiter = EndpointRateLimiter()
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            endpoint = request.endpoint
            ip = request.remote_addr
            
            endpoint_limiter = limiter.get_limiter(endpoint)
            allowed, wait_time = endpoint_limiter.is_allowed(ip)
            
            if not allowed:
                response = {
                    'error': 'Too many requests for this endpoint',
                    'wait_time': wait_time,
                    'endpoint': endpoint
                }
                return jsonify(response), 429
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
