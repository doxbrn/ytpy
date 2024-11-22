from flask import Blueprint, jsonify, request
from utils.validators import validate_url
import yt_dlp
import uuid
from threading import Thread
import os
import time
import random

download_bp = Blueprint('download', __name__)

# Dicionário para armazenar o status dos downloads
downloads = {}

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15'
    ]
    return random.choice(user_agents)

def download_video(task_id, url, format_id=None, quality='best'):
    try:
        downloads[task_id]['status'] = 'downloading'
        
        ydl_opts = {
            'format': f'{format_id}' if format_id else f'{quality}',
            'outtmpl': f'downloads/%(title)s-%(id)s.%(ext)s',
            'progress_hooks': [lambda d: update_progress(task_id, d)],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'http_headers': {
                'User-Agent': get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Primeiro extrai as informações para verificar se o vídeo está disponível
            try:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Não foi possível obter informações do vídeo")
                
                # Se chegou aqui, o vídeo está disponível, então faz o download
                info = ydl.extract_info(url, download=True)
                downloads[task_id]['filename'] = ydl.prepare_filename(info)
                downloads[task_id]['status'] = 'completed'
                downloads[task_id]['error'] = None
                
            except Exception as e:
                raise Exception(f"Erro ao extrair informações: {str(e)}")
            
    except Exception as e:
        downloads[task_id]['status'] = 'error'
        downloads[task_id]['error'] = str(e)
        print(f"Download error for task {task_id}: {str(e)}")

def update_progress(task_id, d):
    if d['status'] == 'downloading':
        try:
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            downloads[task_id]['progress'] = {
                'downloaded_bytes': downloaded,
                'total_bytes': total,
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0),
                'percentage': (downloaded / total * 100) if total > 0 else 0
            }
        except Exception as e:
            print(f"Error updating progress for task {task_id}: {str(e)}")

def cleanup_old_downloads():
    current_time = time.time()
    to_remove = []
    
    for task_id, info in downloads.items():
        # Remove downloads mais antigos que 1 hora
        if current_time - info.get('start_time', current_time) > 3600:
            to_remove.append(task_id)
    
    for task_id in to_remove:
        try:
            if downloads[task_id].get('filename'):
                try:
                    os.remove(downloads[task_id]['filename'])
                except:
                    pass
            del downloads[task_id]
        except:
            pass

@download_bp.route('/download', methods=['POST'])
def start_download():
    cleanup_old_downloads()
    
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL não fornecida'}), 400
        
    url = data['url']
    format_id = data.get('format')
    quality = data.get('quality', 'best')
    
    if not validate_url(url):
        return jsonify({'error': 'URL inválida'}), 400
    
    task_id = str(uuid.uuid4())
    downloads[task_id] = {
        'status': 'pending',
        'url': url,
        'progress': {},
        'filename': None,
        'error': None,
        'start_time': time.time()
    }
    
    # Inicia o download em uma thread separada
    thread = Thread(target=download_video, args=(task_id, url, format_id, quality))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'Download iniciado',
        'task_id': task_id
    }), 202

@download_bp.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    if task_id not in downloads:
        return jsonify({'error': 'Download não encontrado'}), 404
        
    return jsonify(downloads[task_id])

@download_bp.route('/cancel/<task_id>', methods=['POST'])
def cancel_download(task_id):
    if task_id not in downloads:
        return jsonify({'error': 'Download não encontrado'}), 404
        
    if downloads[task_id]['status'] == 'downloading':
        # Tenta cancelar o download removendo o arquivo parcial
        if downloads[task_id].get('filename'):
            try:
                os.remove(downloads[task_id]['filename'])
            except:
                pass
        
        downloads[task_id]['status'] = 'cancelled'
        return jsonify({'message': 'Download cancelado'})
    else:
        return jsonify({'error': 'Download não pode ser cancelado'}), 400
