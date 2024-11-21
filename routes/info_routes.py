from flask import Blueprint, jsonify, request
from utils.validators import validate_url
import yt_dlp

info_bp = Blueprint('info', __name__)

@info_bp.route('/info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400
        
    if not validate_url(url):
        return jsonify({'error': 'URL inválida'}), 400
    
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            
            video_info = {
                'id': info.get('id'),
                'title': info.get('title'),
                'description': info.get('description'),
                'duration': info.get('duration'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'channel': info.get('channel'),
                'channel_id': info.get('channel_id'),
                'upload_date': info.get('upload_date'),
                'thumbnail': info.get('thumbnail'),
            }
            
            return jsonify(video_info)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@info_bp.route('/formats', methods=['GET'])
def get_video_formats():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400
        
    if not validate_url(url):
        return jsonify({'error': 'URL inválida'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            for f in info['formats']:
                format_info = {
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'resolution': f.get('resolution'),
                    'filesize': f.get('filesize'),
                    'vcodec': f.get('vcodec'),
                    'acodec': f.get('acodec'),
                    'format_note': f.get('format_note')
                }
                formats.append(format_info)
            
            return jsonify({'formats': formats})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
