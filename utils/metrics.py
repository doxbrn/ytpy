from prometheus_client import Counter, Histogram, Info
from flask import request
import time

# Métricas
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Latência das requisições HTTP',
    ['method', 'endpoint']
)

DOWNLOAD_COUNT = Counter(
    'youtube_downloads_total',
    'Total de downloads iniciados',
    ['format', 'quality']
)

DOWNLOAD_ERRORS = Counter(
    'youtube_download_errors_total',
    'Total de erros de download',
    ['error_type']
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Total de hits no cache',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total de misses no cache',
    ['cache_type']
)

API_INFO = Info('youtube_api', 'Informações da API do YouTube')

def setup_metrics(app):
    """Configura métricas iniciais"""
    API_INFO.info({
        'version': app.config.get('VERSION', 'unknown'),
        'environment': app.config.get('ENV', 'unknown')
    })

def record_metrics():
    """Registra métricas para cada requisição"""
    # Ignora requisições para métricas
    if request.path == '/metrics':
        return
        
    # Registra tempo de resposta
    request.start_time = time.time()

def record_request_metrics(response):
    """Registra métricas após cada requisição"""
    if not hasattr(request, 'start_time'):
        return response
        
    # Calcula latência
    latency = time.time() - request.start_time
    
    # Registra métricas
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown'
    ).observe(latency)
    
    return response

def record_download_metrics(format_name, quality):
    """Registra métricas de download"""
    DOWNLOAD_COUNT.labels(
        format=format_name,
        quality=quality
    ).inc()

def record_download_error(error_type):
    """Registra erros de download"""
    DOWNLOAD_ERRORS.labels(
        error_type=error_type
    ).inc()

def record_cache_metrics(hit, cache_type='default'):
    """Registra métricas de cache"""
    if hit:
        CACHE_HITS.labels(cache_type=cache_type).inc()
    else:
        CACHE_MISSES.labels(cache_type=cache_type).inc()
