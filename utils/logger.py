import os
import logging
import logging.handlers
import json
from datetime import datetime
from flask import has_request_context, request
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Adiciona campos padrão
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

        # Adiciona informações de request se disponível
        if has_request_context():
            log_record['method'] = request.method
            log_record['path'] = request.path
            log_record['ip'] = request.remote_addr
            log_record['user_agent'] = request.user_agent.string

        # Adiciona informações de exceção se disponível
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }

def setup_logging(app_name='youtube-downloader', log_level=None):
    """Configura logging estruturado"""
    if not log_level:
        log_level = os.getenv('LOG_LEVEL', 'INFO')

    # Cria diretório de logs se não existir
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configura logger raiz
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Configura formato JSON
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para arquivo
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, f'{app_name}.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para erros
    error_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, f'{app_name}-error.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger

def get_logger(name):
    """Retorna um logger configurado para o módulo especificado"""
    return logging.getLogger(name)

# Funções auxiliares para logging estruturado
def log_request_info(logger):
    """Registra informações detalhadas da requisição"""
    if has_request_context():
        logger.info('Request received', extra={
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string,
            'headers': dict(request.headers),
            'args': dict(request.args)
        })

def log_response_info(logger, response):
    """Registra informações detalhadas da resposta"""
    if has_request_context():
        logger.info('Response sent', extra={
            'status_code': response.status_code,
            'content_length': response.content_length,
            'content_type': response.content_type
        })

def log_error(logger, error, context=None):
    """Registra erros com contexto adicional"""
    extra = {'error_type': type(error).__name__}
    if context:
        extra.update(context)
    
    logger.error(str(error), exc_info=True, extra=extra)

def log_download_start(logger, video_id, format_info):
    """Registra início de download"""
    logger.info('Download started', extra={
        'video_id': video_id,
        'format': format_info
    })

def log_download_complete(logger, video_id, duration):
    """Registra conclusão de download"""
    logger.info('Download completed', extra={
        'video_id': video_id,
        'duration_seconds': duration
    })

def log_cache_event(logger, cache_type, hit, key):
    """Registra eventos de cache"""
    logger.debug('Cache access', extra={
        'cache_type': cache_type,
        'hit': hit,
        'key': key
    })
