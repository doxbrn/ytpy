import yt_dlp
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from config import Config

class YouTubeAnalytics:
    def __init__(self):
        self.ydl_opts = Config.YTDL_OPTIONS.copy()
        self.ydl_opts.update({
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True
        })

    def get_channel_info(self, channel_url: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas sobre um canal do YouTube
        
        Args:
            channel_url (str): URL do canal
            
        Returns:
            dict: Informações do canal
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                channel_info = ydl.extract_info(channel_url, download=False)
                
                return {
                    'id': channel_info.get('channel_id'),
                    'name': channel_info.get('channel'),
                    'description': channel_info.get('description'),
                    'subscriber_count': channel_info.get('subscriber_count'),
                    'video_count': channel_info.get('video_count'),
                    'view_count': channel_info.get('view_count'),
                    'channel_url': channel_info.get('channel_url'),
                    'thumbnails': channel_info.get('thumbnails'),
                    'country': channel_info.get('country'),
                    'joined_date': channel_info.get('upload_date'),
                    'categories': channel_info.get('categories', []),
                    'tags': channel_info.get('tags', [])
                }
        except Exception as e:
            raise Exception(f"Erro ao obter informações do canal: {str(e)}")

    def get_channel_videos(self, channel_url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtém lista de vídeos de um canal
        
        Args:
            channel_url (str): URL do canal
            limit (int): Número máximo de vídeos para retornar
            
        Returns:
            list: Lista de vídeos do canal
        """
        try:
            opts = self.ydl_opts.copy()
            opts.update({
                'extract_flat': 'in_playlist',
                'playlistend': limit
            })
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                playlist = ydl.extract_info(f"{channel_url}/videos", download=False)
                
                videos = []
                for entry in playlist['entries'][:limit]:
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'description': entry.get('description'),
                        'duration': entry.get('duration'),
                        'view_count': entry.get('view_count'),
                        'like_count': entry.get('like_count'),
                        'comment_count': entry.get('comment_count'),
                        'upload_date': entry.get('upload_date'),
                        'thumbnails': entry.get('thumbnails'),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id')}"
                    })
                    
                return videos
        except Exception as e:
            raise Exception(f"Erro ao obter vídeos do canal: {str(e)}")

    def get_video_metrics(self, video_id: str) -> Dict[str, Any]:
        """
        Obtém métricas detalhadas de um vídeo
        
        Args:
            video_id (str): ID do vídeo
            
        Returns:
            dict: Métricas do vídeo
        """
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
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
                    'technical': {
                        'formats': len(info.get('formats', [])),
                        'available_qualities': [
                            f['format_note'] 
                            for f in info.get('formats', []) 
                            if f.get('format_note')
                        ],
                        'filesize_approx': info.get('filesize_approx'),
                        'resolution': info.get('resolution')
                    },
                    'metadata': {
                        'categories': info.get('categories', []),
                        'tags': info.get('tags', []),
                        'language': info.get('language'),
                        'age_restricted': info.get('age_restricted', False)
                    }
                }
        except Exception as e:
            raise Exception(f"Erro ao obter métricas do vídeo: {str(e)}")

    def get_channel_statistics(self, channel_url: str) -> Dict[str, Any]:
        """
        Calcula estatísticas gerais do canal baseado nos últimos vídeos
        
        Args:
            channel_url (str): URL do canal
            
        Returns:
            dict: Estatísticas do canal
        """
        try:
            videos = self.get_channel_videos(channel_url, limit=30)  # Últimos 30 vídeos
            
            if not videos:
                return {}
                
            total_views = sum(v.get('view_count', 0) for v in videos)
            total_likes = sum(v.get('like_count', 0) for v in videos)
            total_comments = sum(v.get('comment_count', 0) for v in videos)
            
            return {
                'video_metrics': {
                    'total_videos_analyzed': len(videos),
                    'average_views': total_views / len(videos),
                    'average_likes': total_likes / len(videos),
                    'average_comments': total_comments / len(videos),
                    'engagement_rate': (total_likes + total_comments) / total_views if total_views > 0 else 0
                },
                'upload_frequency': self._calculate_upload_frequency(videos),
                'best_performing_video': max(videos, key=lambda x: x.get('view_count', 0)),
                'recent_performance': self._analyze_recent_performance(videos)
            }
        except Exception as e:
            raise Exception(f"Erro ao calcular estatísticas do canal: {str(e)}")

    def _calculate_upload_frequency(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula a frequência de upload do canal
        """
        if len(videos) < 2:
            return {'average_days_between_uploads': None}
            
        upload_dates = [
            datetime.strptime(v['upload_date'], '%Y%m%d')
            for v in videos
            if v.get('upload_date')
        ]
        upload_dates.sort(reverse=True)
        
        intervals = [
            (upload_dates[i] - upload_dates[i+1]).days
            for i in range(len(upload_dates)-1)
        ]
        
        return {
            'average_days_between_uploads': sum(intervals) / len(intervals),
            'most_active_month': max(upload_dates, key=lambda x: upload_dates.count(x.strftime('%Y-%m'))).strftime('%Y-%m'),
            'total_uploads_analyzed': len(videos)
        }

    def _analyze_recent_performance(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa o desempenho recente do canal
        """
        if len(videos) < 5:
            return {}
            
        recent_videos = videos[:5]  # 5 vídeos mais recentes
        older_videos = videos[5:15]  # 10 vídeos anteriores
        
        recent_avg_views = sum(v.get('view_count', 0) for v in recent_videos) / len(recent_videos)
        older_avg_views = sum(v.get('view_count', 0) for v in older_videos) / len(older_videos)
        
        return {
            'recent_videos_avg_views': recent_avg_views,
            'older_videos_avg_views': older_avg_views,
            'growth_rate': ((recent_avg_views - older_avg_views) / older_avg_views) * 100 if older_avg_views > 0 else 0,
            'trending_topics': self._extract_trending_topics(recent_videos)
        }

    def _extract_trending_topics(self, videos: List[Dict[str, Any]]) -> List[str]:
        """
        Extrai tópicos populares dos títulos dos vídeos
        """
        # Implementação básica - pode ser melhorada com NLP
        all_words = ' '.join([v.get('title', '').lower() for v in videos]).split()
        word_count = {}
        
        for word in all_words:
            if len(word) > 3:  # Ignorar palavras muito curtas
                word_count[word] = word_count.get(word, 0) + 1
                
        return sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]
