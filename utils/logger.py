import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

class Logger:
    def __init__(self, name: str, log_dir: str = 'logs'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Configurar logger principal
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para arquivo de log geral
        general_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        general_handler.setLevel(logging.INFO)
        general_handler.setFormatter(formatter)
        
        # Handler para erros
        error_handler = RotatingFileHandler(
            os.path.join(log_dir, 'error.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Handler para downloads
        download_handler = RotatingFileHandler(
            os.path.join(log_dir, 'downloads.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        download_handler.setLevel(logging.INFO)
        download_handler.setFormatter(formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        # Adicionar handlers ao logger
        self.logger.addHandler(general_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(download_handler)
        self.logger.addHandler(console_handler)
        
        # Filtros personalizados
        download_handler.addFilter(self.DownloadFilter())
        
    class DownloadFilter(logging.Filter):
        def filter(self, record):
            return 'download' in record.getMessage().lower()
            
    def log_download_start(self, video_id: str, format: str) -> None:
        """Log início de download"""
        self.logger.info(
            f"Download iniciado - Video: {video_id}, Format: {format}"
        )
        
    def log_download_complete(self, video_id: str, file_path: str) -> None:
        """Log download completo"""
        self.logger.info(
            f"Download completo - Video: {video_id}, Path: {file_path}"
        )
        
    def log_download_error(self, video_id: str, error: str) -> None:
        """Log erro no download"""
        self.logger.error(
            f"Erro no download - Video: {video_id}, Error: {error}"
        )
        
    def log_api_request(self, method: str, endpoint: str, params: dict) -> None:
        """Log requisição à API"""
        self.logger.info(
            f"API Request - Method: {method}, Endpoint: {endpoint}, "
            f"Params: {params}"
        )
        
    def log_api_response(self, endpoint: str, status: int, 
                        response_time: float) -> None:
        """Log resposta da API"""
        self.logger.info(
            f"API Response - Endpoint: {endpoint}, Status: {status}, "
            f"Time: {response_time:.2f}s"
        )
        
    def log_error(self, error: Exception, context: str = None) -> None:
        """Log erro genérico"""
        if context:
            self.logger.error(f"Error in {context}: {str(error)}")
        else:
            self.logger.error(str(error))
            
    def log_warning(self, message: str) -> None:
        """Log aviso"""
        self.logger.warning(message)
        
    def log_info(self, message: str) -> None:
        """Log informação"""
        self.logger.info(message)
        
    def log_debug(self, message: str) -> None:
        """Log debug"""
        self.logger.debug(message)
