import os
import json
import time
from typing import Any, Optional

class CacheManager:
    def __init__(self, cache_dir: str = 'cache'):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_cache_path(self, key: str) -> str:
        """Gera o caminho do arquivo de cache para uma chave"""
        # Substitui caracteres inválidos no nome do arquivo
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return os.path.join(self.cache_dir, f"{safe_key}.json")

    def get(self, key: str) -> Optional[Any]:
        """Obtém um valor do cache"""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                
            # Verifica se o cache expirou
            if time.time() > data.get('expires_at', 0):
                self.delete(key)
                return None
                
            return data.get('value')
        except Exception as e:
            print(f"Erro ao ler cache: {str(e)}")
            return None

    def set(self, key: str, value: Any, expires_in: int = 3600) -> bool:
        """
        Armazena um valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            expires_in: Tempo de expiração em segundos (padrão: 1 hora)
        """
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                'value': value,
                'expires_at': time.time() + expires_in
            }
            
            with open(cache_path, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Erro ao escrever cache: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Remove um valor do cache"""
        cache_path = self._get_cache_path(key)
        
        try:
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return True
        except Exception as e:
            print(f"Erro ao deletar cache: {str(e)}")
            return False

    def clear(self) -> bool:
        """Limpa todo o cache"""
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            return True
        except Exception as e:
            print(f"Erro ao limpar cache: {str(e)}")
            return False

    def cleanup_expired(self) -> int:
        """
        Remove todos os itens expirados do cache
        Retorna o número de itens removidos
        """
        removed = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    if time.time() > data.get('expires_at', 0):
                        os.remove(file_path)
                        removed += 1
                except:
                    # Se houver erro ao ler o arquivo, remove-o
                    os.remove(file_path)
                    removed += 1
                    
            return removed
        except Exception as e:
            print(f"Erro ao limpar cache expirado: {str(e)}")
            return removed
