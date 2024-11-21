import re
from urllib.parse import urlparse

def validate_url(url):
    """
    Valida se a URL é uma URL válida do YouTube
    
    Args:
        url (str): URL para validar
        
    Returns:
        bool: True se a URL é válida, False caso contrário
    """
    try:
        # Verifica se a URL é válida
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False
            
        # Verifica se é uma URL do YouTube
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        
        youtube_regex_match = re.match(youtube_regex, url)
        return youtube_regex_match is not None
        
    except:
        return False

def validate_format(format):
    """
    Valida se o formato solicitado é suportado
    
    Args:
        format (str): Formato para validar
        
    Returns:
        bool: True se o formato é válido, False caso contrário
    """
    return format.lower() in ['mp4', 'mp3', 'webm']

def validate_quality(quality):
    """
    Valida se a qualidade solicitada é suportada
    
    Args:
        quality (str): Qualidade para validar
        
    Returns:
        bool: True se a qualidade é válida, False caso contrário
    """
    if quality == 'best':
        return True
        
    try:
        height = int(quality)
        return height in [144, 240, 360, 480, 720, 1080, 1440, 2160]
    except:
        return False
