import threading
import yt_dlp
from typing import Dict, Any
import time
import os

class DownloadManager:
    def __init__(self):
        self.downloads: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def start_download(self, task_id: str, url: str, options: dict) -> None:
        """
        Inicia um novo download em uma thread separada
        
        Args:
            task_id (str): ID único da tarefa
            url (str): URL do vídeo
            options (dict): Opções do yt-dlp
        """
        def progress_hook(d):
            if d['status'] == 'downloading':
                with self.lock:
                    self.downloads[task_id].update({
                        'status': 'downloading',
                        'downloaded_bytes': d.get('downloaded_bytes', 0),
                        'total_bytes': d.get('total_bytes', 0),
                        'speed': d.get('speed', 0),
                        'eta': d.get('eta', 0),
                        'progress': d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
                        if d.get('total_bytes', 0) > 0 else 0
                    })
            elif d['status'] == 'finished':
                with self.lock:
                    self.downloads[task_id].update({
                        'status': 'processing',
                        'progress': 100
                    })
            elif d['status'] == 'error':
                with self.lock:
                    self.downloads[task_id].update({
                        'status': 'error',
                        'error': str(d.get('error', 'Unknown error'))
                    })

        def download_thread():
            try:
                ydl_opts = options.copy()
                ydl_opts['progress_hooks'] = [progress_hook]
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
                with self.lock:
                    self.downloads[task_id].update({
                        'status': 'completed',
                        'progress': 100,
                        'completed_at': time.time()
                    })
            except Exception as e:
                with self.lock:
                    self.downloads[task_id].update({
                        'status': 'error',
                        'error': str(e)
                    })

        with self.lock:
            self.downloads[task_id] = {
                'url': url,
                'status': 'starting',
                'progress': 0,
                'started_at': time.time()
            }

        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()

    def get_status(self, task_id: str) -> Dict[str, Any]:
        """
        Obtém o status de um download
        
        Args:
            task_id (str): ID da tarefa
            
        Returns:
            dict: Status do download ou None se não encontrado
        """
        with self.lock:
            return self.downloads.get(task_id)

    def cancel_download(self, task_id: str) -> bool:
        """
        Cancela um download em andamento
        
        Args:
            task_id (str): ID da tarefa
            
        Returns:
            bool: True se o download foi cancelado, False caso contrário
        """
        with self.lock:
            if task_id in self.downloads:
                self.downloads[task_id]['status'] = 'cancelled'
                return True
            return False

    def cleanup_old_downloads(self, max_age_hours: int = 24) -> None:
        """
        Remove downloads antigos da memória
        
        Args:
            max_age_hours (int): Idade máxima em horas para manter os downloads
        """
        current_time = time.time()
        with self.lock:
            for task_id in list(self.downloads.keys()):
                download = self.downloads[task_id]
                if download['status'] in ['completed', 'error', 'cancelled']:
                    started_at = download.get('started_at', 0)
                    if current_time - started_at > max_age_hours * 3600:
                        del self.downloads[task_id]
