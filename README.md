# YouTube Downloader API

Uma API RESTful para download de vídeos do YouTube usando yt-dlp.

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o servidor:
```bash
python app.py
```

## Endpoints

### GET /api/info/{video_id}
Retorna informações sobre um vídeo específico.

### POST /api/download
Faz o download de um vídeo do YouTube.
Parâmetros no corpo da requisição:
- url: URL do vídeo
- format: Formato desejado (mp4, mp3)
- quality: Qualidade do vídeo (best, worst, etc)

### GET /api/status/{task_id}
Verifica o status de um download em andamento.

## Configuração

O servidor roda por padrão na porta 5000. Você pode modificar as configurações no arquivo .env
