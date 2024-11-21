from flask import Blueprint, jsonify, request
from utils.validators import validate_url
import yt_dlp
import uuid
from threading import Thread
import os

download_bp = Blueprint('download', __name__)

# Dicionário para armazenar o status dos downloads
downloads = {}

def download_video(task_id, url, format_id=None, quality='best'):
    try:
        downloads[task_id]['status'] = 'downloading'
        
        ydl_opts = {
            'format': f'{format_id}' if format_id else f'{quality}',
            'outtmpl': f'downloads/%(title)s-%(id)s.%(ext)s',
            'progress_hooks': [lambda d: update_progress(task_id, d)],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloads[task_id]['filename'] = ydl.prepare_filename(info)
            downloads[task_id]['status'] = 'completed'
            
    except Exception as e:
        downloads[task_id]['status'] = 'error'
        downloads[task_id]['error'] = str(e)

def update_progress(task_id, d):
    if d['status'] == 'downloading':
        try:
            downloads[task_id]['progress'] = {
                'downloaded_bytes': d.get('downloaded_bytes', 0),
                'total_bytes': d.get('total_bytes', 0),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0),
                'percentage': d.get('percentage', 0)
            }
        except KeyError:
            pass

@download_bp.route('/download', methods=['POST'])
def start_download():
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
        'error': None
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
