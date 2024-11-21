from flask import Flask
from flask_cors import CORS
from routes.download_routes import download_bp
from routes.info_routes import info_bp
from routes.analytics_routes import analytics_bp
from config import Config

app = Flask(__name__)
CORS(app)

# Registrando as blueprints
app.register_blueprint(download_bp, url_prefix='/api')
app.register_blueprint(info_bp, url_prefix='/api')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

# Configurações da aplicação
app.config.from_object(Config)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube Downloader Server')
    parser.add_argument('--port', type=int, default=5000, help='Porta do servidor (padrão: 5000)')
    args = parser.parse_args()
    
    app.run(host='0.0.0.0', debug=True, port=args.port)
