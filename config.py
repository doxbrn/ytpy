import os
from datetime import timedelta

class Config:
    """Configuração base"""
    # Configurações básicas
    VERSION = '1.0.0'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')
    
    # Configurações de ambiente
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = False
    TESTING = False
    
    # Configurações de segurança
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Configurações CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_MAX_AGE = 600
    
    # Configurações de Rate Limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # Configurações de Cache
    CACHE_TYPE = 'filesystem'
    CACHE_DIR = 'cache'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_THRESHOLD = 1000
    
    # Configurações de Download
    DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
    MAX_DOWNLOAD_SIZE = 1024 * 1024 * 1024  # 1GB
    SUPPORTED_FORMATS = ['mp4', 'webm', 'mp3', 'm4a']
    DEFAULT_FORMAT = 'mp4'
    
    # Configurações de Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DIR = 'logs'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    
    # Configurações de Métricas
    ENABLE_METRICS = True
    METRICS_PORT = 9090
    
    # Configurações de Timeout
    REQUEST_TIMEOUT = 30
    DOWNLOAD_TIMEOUT = 3600  # 1 hora
    
    @staticmethod
    def init_app(app):
        """Inicializa a aplicação com configurações base"""
        # Criar diretórios necessários
        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(Config.CACHE_DIR, exist_ok=True)
        os.makedirs(Config.LOG_DIR, exist_ok=True)

class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    ENV = 'development'
    DEBUG = True
    
    # Configurações de segurança mais permissivas
    SESSION_COOKIE_SECURE = False
    CORS_ORIGINS = ['*']
    
    # Rate limiting mais permissivo
    RATELIMIT_DEFAULT = "1000 per day"
    
    # Cache em memória
    CACHE_TYPE = 'simple'
    
    # Logging mais detalhado
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Configuração de testes"""
    ENV = 'testing'
    TESTING = True
    DEBUG = True
    
    # Desabilita segurança para testes
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    
    # Cache em memória
    CACHE_TYPE = 'null'
    
    # Diretórios temporários
    DOWNLOAD_DIR = '/tmp/downloads'
    CACHE_DIR = '/tmp/cache'
    LOG_DIR = '/tmp/logs'
    
    # Logging mínimo
    LOG_LEVEL = 'ERROR'
    
    # Desabilita métricas
    ENABLE_METRICS = False

class ProductionConfig(Config):
    """Configuração de produção"""
    ENV = 'production'
    
    # Configurações de segurança mais restritas
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # CORS mais restrito
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    
    # Rate limiting mais restrito
    RATELIMIT_DEFAULT = "100 per day"
    
    # Cache distribuído
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
    
    # Logging mais restrito
    LOG_LEVEL = 'WARNING'
    
    # Timeouts mais curtos
    REQUEST_TIMEOUT = 15
    DOWNLOAD_TIMEOUT = 1800  # 30 minutos

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
