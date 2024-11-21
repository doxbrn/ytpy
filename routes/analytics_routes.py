from flask import Blueprint, jsonify, request
from utils.analytics import YouTubeAnalytics
from utils.validators import validate_url

analytics_bp = Blueprint('analytics', __name__)
youtube_analytics = YouTubeAnalytics()

@analytics_bp.route('/channel/info', methods=['GET'])
def get_channel_info():
    """
    Obtém informações detalhadas sobre um canal
    ---
    parameters:
      - name: url
        in: query
        required: true
        type: string
        description: URL do canal do YouTube
    responses:
      200:
        description: Informações do canal obtidas com sucesso
      400:
        description: URL inválida
      500:
        description: Erro interno do servidor
    """
    channel_url = request.args.get('url')
    if not channel_url or not validate_url(channel_url):
        return jsonify({'error': 'URL do canal inválida'}), 400

    try:
        info = youtube_analytics.get_channel_info(channel_url)
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/channel/videos', methods=['GET'])
def get_channel_videos():
    """
    Obtém lista de vídeos de um canal
    ---
    parameters:
      - name: url
        in: query
        required: true
        type: string
        description: URL do canal do YouTube
      - name: limit
        in: query
        required: false
        type: integer
        description: Número máximo de vídeos para retornar
        default: 50
    responses:
      200:
        description: Lista de vídeos obtida com sucesso
      400:
        description: URL inválida
      500:
        description: Erro interno do servidor
    """
    channel_url = request.args.get('url')
    limit = request.args.get('limit', 50, type=int)

    if not channel_url or not validate_url(channel_url):
        return jsonify({'error': 'URL do canal inválida'}), 400

    try:
        videos = youtube_analytics.get_channel_videos(channel_url, limit)
        return jsonify(videos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/video/metrics/<video_id>', methods=['GET'])
def get_video_metrics(video_id):
    """
    Obtém métricas detalhadas de um vídeo
    ---
    parameters:
      - name: video_id
        in: path
        required: true
        type: string
        description: ID do vídeo do YouTube
    responses:
      200:
        description: Métricas do vídeo obtidas com sucesso
      400:
        description: ID do vídeo inválido
      500:
        description: Erro interno do servidor
    """
    if not video_id:
        return jsonify({'error': 'ID do vídeo inválido'}), 400

    try:
        metrics = youtube_analytics.get_video_metrics(video_id)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/channel/statistics', methods=['GET'])
def get_channel_statistics():
    """
    Obtém estatísticas gerais de um canal
    ---
    parameters:
      - name: url
        in: query
        required: true
        type: string
        description: URL do canal do YouTube
    responses:
      200:
        description: Estatísticas do canal obtidas com sucesso
      400:
        description: URL inválida
      500:
        description: Erro interno do servidor
    """
    channel_url = request.args.get('url')
    if not channel_url or not validate_url(channel_url):
        return jsonify({'error': 'URL do canal inválida'}), 400

    try:
        stats = youtube_analytics.get_channel_statistics(channel_url)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/channel/performance', methods=['GET'])
def get_channel_performance():
    """
    Obtém análise de desempenho do canal
    ---
    parameters:
      - name: url
        in: query
        required: true
        type: string
        description: URL do canal do YouTube
    responses:
      200:
        description: Análise de desempenho obtida com sucesso
      400:
        description: URL inválida
      500:
        description: Erro interno do servidor
    """
    channel_url = request.args.get('url')
    if not channel_url or not validate_url(channel_url):
        return jsonify({'error': 'URL do canal inválida'}), 400

    try:
        # Obtém estatísticas completas e filtra apenas as métricas de desempenho
        stats = youtube_analytics.get_channel_statistics(channel_url)
        performance = {
            'recent_performance': stats.get('recent_performance', {}),
            'upload_frequency': stats.get('upload_frequency', {}),
            'engagement_metrics': stats.get('video_metrics', {})
        }
        return jsonify(performance)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
