import json
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, cache_dir: str = 'cache', expiration_hours: int = 24):
        self.cache_dir = cache_dir
        self.expiration_delta = timedelta(hours=expiration_hours)
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_path(self, key: str) -> str:
        """Gera o caminho do arquivo de cache para uma chave"""
        return os.path.join(self.cache_dir, f"{key}.json")

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Recupera dados do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Dados armazenados ou None se não encontrado/expirado
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
                
            # Verifica se o cache expirou
            cached_time = datetime.fromisoformat(cached_data['cached_at'])
            if datetime.now() - cached_time > self.expiration_delta:
                os.remove(cache_path)
                return None
                
            return cached_data['data']
        except:
            return None

    def set(self, key: str, data: Dict[str, Any]) -> None:
        """
        Armazena dados no cache
        
        Args:
            key: Chave do cache
            data: Dados para armazenar
        """
        cache_path = self._get_cache_path(key)
        
        cache_data = {
            'data': data,
            'cached_at': datetime.now().isoformat()
        }
        
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)

    def invalidate(self, key: str) -> None:
        """
        Remove um item específico do cache
        
        Args:
            key: Chave do cache para remover
        """
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            os.remove(cache_path)

    def clear(self) -> None:
        """Remove todos os itens do cache"""
        for file in os.listdir(self.cache_dir):
            if file.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, file))

    def cleanup_expired(self) -> None:
        """Remove todos os itens expirados do cache"""
        for file in os.listdir(self.cache_dir):
            if not file.endswith('.json'):
                continue
                
            cache_path = os.path.join(self.cache_dir, file)
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                    
                cached_time = datetime.fromisoformat(cached_data['cached_at'])
                if datetime.now() - cached_time > self.expiration_delta:
                    os.remove(cache_path)
            except:
                # Remove arquivos corrompidos
                os.remove(cache_path)
