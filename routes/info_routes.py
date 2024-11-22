from flask import Blueprint, jsonify, request
from utils.validators import validate_url
import yt_dlp
from utils.cache_manager import CacheManager
from datetime import datetime

info_bp = Blueprint('info', __name__)
cache = CacheManager()

def get_yt_info(url, extract_subtitles=False):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,  # Mudado para False para obter todos os dados
        'writesubtitles': extract_subtitles,
        'writeautomaticsub': extract_subtitles,
        'subtitleslangs': ['en', 'pt', 'es'],
        'get_all_subtitles': True,
        'writethumbnail': True,
        'writeinfojson': True,
        'writedescription': True,
        'writecomments': True,
        'getcomments': True,
        'ignoreerrors': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            print(f"Error extracting info: {str(e)}")
            return None

def format_duration(seconds):
    if not seconds:
        return None
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def format_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
    except:
        return date_str

@info_bp.route('/info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    if not url or not validate_url(url):
        return jsonify({'error': 'URL inválida'}), 400
    
    # Tenta obter do cache primeiro
    cached_info = cache.get(f'info_{url}')
    if cached_info:
        return jsonify(cached_info)
    
    info = get_yt_info(url)
    if not info:
        return jsonify({'error': 'Não foi possível obter informações do vídeo'}), 500
    
    # Extrai todos os dados possíveis do vídeo
    video_info = {
        # Informações Básicas
        'id': info.get('id'),
        'title': info.get('title'),
        'description': info.get('description'),
        'duration': {
            'seconds': info.get('duration'),
            'formatted': format_duration(info.get('duration'))
        },
        'webpage_url': info.get('webpage_url'),
        'original_url': info.get('original_url'),
        
        # Estatísticas
        'view_count': info.get('view_count'),
        'like_count': info.get('like_count'),
        'dislike_count': info.get('dislike_count'),
        'repost_count': info.get('repost_count'),
        'average_rating': info.get('average_rating'),
        'comment_count': info.get('comment_count'),
        
        # Informações do Canal
        'channel': {
            'id': info.get('channel_id'),
            'name': info.get('channel'),
            'url': info.get('channel_url'),
            'follower_count': info.get('channel_follower_count'),
            'subscriber_count': info.get('subscriber_count'),
            'description': info.get('channel_description'),
            'verified': info.get('channel_is_verified', False)
        },
        
        # Datas
        'upload_date': format_date(info.get('upload_date')),
        'modified_date': format_date(info.get('modified_date')),
        'release_date': format_date(info.get('release_date')),
        
        # Metadados
        'categories': info.get('categories', []),
        'tags': info.get('tags', []),
        'language': info.get('language'),
        'languages': info.get('languages', []),
        'location': info.get('location'),
        'duration_string': info.get('duration_string'),
        'format': info.get('format'),
        'format_id': info.get('format_id'),
        'format_note': info.get('format_note'),
        
        # Thumbnails
        'thumbnails': info.get('thumbnails', []),
        'thumbnail': info.get('thumbnail'),  # Thumbnail principal
        
        # Informações Técnicas
        'width': info.get('width'),
        'height': info.get('height'),
        'resolution': info.get('resolution'),
        'fps': info.get('fps'),
        'dynamic_range': info.get('dynamic_range'),
        'vcodec': info.get('vcodec'),
        'acodec': info.get('acodec'),
        'abr': info.get('abr'),  # Audio bitrate
        'vbr': info.get('vbr'),  # Video bitrate
        
        # Status e Flags
        'is_live': info.get('is_live', False),
        'was_live': info.get('was_live', False),
        'live_status': info.get('live_status'),
        'age_restricted': info.get('age_restricted', False),
        'availability': info.get('availability'),
        'playable_in_embed': info.get('playable_in_embed', True),
        'is_ads_enabled': info.get('is_ads_enabled', False),
        
        # Chapters e Segmentos
        'chapters': info.get('chapters', []),
        'segments': info.get('segments', []),
        
        # Legendas e Transcrições
        'automatic_captions': info.get('automatic_captions', {}),
        'subtitles': info.get('subtitles', {}),
        'has_subtitles': bool(info.get('subtitles')),
        'has_auto_subtitles': bool(info.get('automatic_captions')),
        
        # Informações de Licença e Copyright
        'license': info.get('license'),
        'creator': info.get('creator'),
        'artist': info.get('artist'),
        'track': info.get('track'),
        'album': info.get('album'),
        'release_year': info.get('release_year'),
        
        # Estatísticas Estendidas
        'start_time': info.get('start_time'),
        'end_time': info.get('end_time'),
        'extractor': info.get('extractor'),
        'extractor_key': info.get('extractor_key'),
        'display_id': info.get('display_id'),
        
        # Informações de Playlist (se aplicável)
        'playlist': info.get('playlist'),
        'playlist_id': info.get('playlist_id'),
        'playlist_title': info.get('playlist_title'),
        'playlist_index': info.get('playlist_index'),
        
        # Comentários (se disponíveis)
        'comments': info.get('comments', []),
        
        # URLs relacionadas
        'related_videos': [{
            'id': v.get('id'),
            'title': v.get('title'),
            'duration': format_duration(v.get('duration')),
            'view_count': v.get('view_count'),
            'thumbnail': v.get('thumbnail'),
            'channel': v.get('channel'),
            'url': v.get('url')
        } for v in info.get('related_videos', [])[:10]],  # Limitado a 10 vídeos relacionados
        
        # Formatos disponíveis
        'formats': [{
            'format_id': f.get('format_id'),
            'ext': f.get('ext'),
            'resolution': f.get('resolution'),
            'filesize': f.get('filesize'),
            'tbr': f.get('tbr'),  # Total bitrate
            'protocol': f.get('protocol'),
            'vcodec': f.get('vcodec'),
            'acodec': f.get('acodec'),
            'asr': f.get('asr'),  # Audio sampling rate
            'format_note': f.get('format_note'),
            'quality': f.get('quality'),
            'fps': f.get('fps'),
            'has_drm': f.get('has_drm', False),
            'url': f.get('url')
        } for f in info.get('formats', [])]
    }
    
    # Cache por 1 hora
    cache.set(f'info_{url}', video_info, 3600)
    return jsonify(video_info)

@info_bp.route('/formats', methods=['GET'])
def get_formats():
    url = request.args.get('url')
    if not url or not validate_url(url):
        return jsonify({'error': 'URL inválida'}), 400
        
    info = get_yt_info(url)
    if not info:
        return jsonify({'error': 'Não foi possível obter informações do vídeo'}), 500
    
    formats = []
    for f in info.get('formats', []):
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

@info_bp.route('/subtitles', methods=['GET'])
def get_subtitles():
    url = request.args.get('url')
    if not url or not validate_url(url):
        return jsonify({'error': 'URL inválida'}), 400
    
    # Tenta obter do cache primeiro
    cached_subs = cache.get(f'subs_{url}')
    if cached_subs:
        return jsonify(cached_subs)
    
    info = get_yt_info(url, extract_subtitles=True)
    if not info:
        return jsonify({'error': 'Não foi possível obter informações do vídeo'}), 500
    
    subtitles = {
        'manual': info.get('subtitles', {}),
        'automatic': info.get('automatic_captions', {})
    }
    
    # Cache por 24 horas
    cache.set(f'subs_{url}', subtitles, 86400)
    return jsonify(subtitles)

@info_bp.route('/transcript', methods=['GET'])
def get_transcript():
    url = request.args.get('url')
    lang = request.args.get('lang', 'en')  # Língua padrão: inglês
    
    if not url or not validate_url(url):
        return jsonify({'error': 'URL inválida'}), 400
    
    # Tenta obter do cache primeiro
    cache_key = f'transcript_{url}_{lang}'
    cached_transcript = cache.get(cache_key)
    if cached_transcript:
        return jsonify(cached_transcript)
    
    info = get_yt_info(url, extract_subtitles=True)
    if not info:
        return jsonify({'error': 'Não foi possível obter informações do vídeo'}), 500
    
    # Tenta obter legendas manuais primeiro, depois automáticas
    subtitles = info.get('subtitles', {})
    auto_subtitles = info.get('automatic_captions', {})
    
    transcript = None
    if lang in subtitles:
        transcript = subtitles[lang]
    elif lang in auto_subtitles:
        transcript = auto_subtitles[lang]
    
    if not transcript:
        return jsonify({
            'error': f'Transcrição não disponível para o idioma {lang}',
            'available_languages': list(set(list(subtitles.keys()) + list(auto_subtitles.keys())))
        }), 404
    
    # Formata a transcrição
    formatted_transcript = {
        'language': lang,
        'is_generated': lang in auto_subtitles,
        'segments': transcript
    }
    
    # Cache por 24 horas
    cache.set(cache_key, formatted_transcript, 86400)
    return jsonify(formatted_transcript)

@info_bp.route('/analytics/video/metrics/<video_id>', methods=['GET'])
def get_video_metrics(video_id):
    url = f'https://www.youtube.com/watch?v={video_id}'
    
    # Tenta obter do cache primeiro
    cached_metrics = cache.get(f'metrics_{video_id}')
    if cached_metrics:
        return jsonify(cached_metrics)
    
    info = get_yt_info(url)
    if not info:
        return jsonify({'error': 'Não foi possível obter métricas do vídeo'}), 500
    
    metrics = {
        'basic_info': {
            'title': info.get('title'),
            'channel': info.get('channel'),
            'channel_id': info.get('channel_id'),
            'duration': info.get('duration'),
            'upload_date': info.get('upload_date')
        },
        'engagement': {
            'view_count': info.get('view_count'),
            'like_count': info.get('like_count'),
            'comment_count': info.get('comment_count'),
            'average_rating': info.get('average_rating')
        },
        'metadata': {
            'tags': info.get('tags', []),
            'categories': info.get('categories', []),
            'language': info.get('language'),
            'age_restricted': info.get('age_restricted', False)
        },
        'technical': {
            'available_qualities': [f.get('format_note') for f in info.get('formats', []) if f.get('format_note')],
            'formats': len(info.get('formats', [])),
            'resolution': info.get('resolution'),
            'filesize_approx': info.get('filesize_approx')
        }
    }
    
    # Cache por 1 hora
    cache.set(f'metrics_{video_id}', metrics, 3600)
    return jsonify(metrics)

@info_bp.route('/analytics/channel/info', methods=['GET'])
def get_channel_info():
    url = request.args.get('url')
    if not url or not validate_url(url):
        return jsonify({'error': 'URL inválida'}), 400
    
    # Tenta obter do cache primeiro
    cached_info = cache.get(f'channel_{url}')
    if cached_info:
        return jsonify(cached_info)
    
    info = get_yt_info(url)
    if not info:
        return jsonify({'error': 'Não foi possível obter informações do canal'}), 500
    
    channel_info = {
        'id': info.get('id'),
        'name': info.get('channel'),
        'description': info.get('description'),
        'channel_url': info.get('channel_url'),
        'subscriber_count': info.get('subscriber_count'),
        'video_count': info.get('video_count'),
        'view_count': info.get('view_count'),
        'joined_date': info.get('joined_date'),
        'country': info.get('country'),
        'thumbnails': info.get('thumbnails', []),
        'tags': info.get('tags', []),
        'categories': info.get('categories', [])
    }
    
    # Cache por 6 horas
    cache.set(f'channel_{url}', channel_info, 21600)
    return jsonify(channel_info)
