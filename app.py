import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from routes.download_routes import download_bp
from routes.info_routes import info_bp
from routes.analytics_routes import analytics_bp
from utils.logger import setup_logging
from utils.metrics import setup_metrics, record_metrics
from config import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
        
    # Inicializa o logger
    setup_logging()
    
    # Cria a aplicação Flask
    app = Flask(__name__)
    
    # Carrega configurações
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Configura CORS
    CORS(app, 
         resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}},
         methods=app.config['CORS_METHODS'],
         allow_headers=app.config['CORS_ALLOW_HEADERS'],
         max_age=app.config['CORS_MAX_AGE'])
    
    # Configura Rate Limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[app.config['RATELIMIT_DEFAULT']],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )
    
    # Configura proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Configura métricas Prometheus se habilitado
    if app.config['ENABLE_METRICS']:
        app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
            '/metrics': make_wsgi_app()
        })
        setup_metrics(app)
    
    # Registra as blueprints
    app.register_blueprint(download_bp, url_prefix='/api')
    app.register_blueprint(info_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Configura handlers de erro
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not Found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal Server Error'}), 500
        
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    # Middleware para métricas
    @app.before_request
    def before_request():
        record_metrics()
    
    return app

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube Downloader Server')
    parser.add_argument('--port', type=int, default=5000, help='Porta do servidor (padrão: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host do servidor (padrão: 0.0.0.0)')
    parser.add_argument('--env', type=str, default='development', help='Ambiente (development/production)')
    args = parser.parse_args()
    
    # Configura variáveis de ambiente
    os.environ['FLASK_ENV'] = args.env
    
    # Cria e executa a aplicação
    app = create_app()
    app.run(host=args.host, port=args.port)
