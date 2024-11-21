# Documentação das Rotas da API

Este documento lista todas as rotas disponíveis na API do YouTube Downloader, incluindo exemplos de uso e respostas.

## Índice
- [Download de Vídeos](#download-de-vídeos)
- [Informações de Vídeos](#informações-de-vídeos)
- [Análise de Canais](#análise-de-canais)
- [Métricas de Vídeos](#métricas-de-vídeos)

## Download de Vídeos

### Iniciar Download
```http
POST /api/download
```

Inicia o download de um vídeo do YouTube.

**Parâmetros (JSON)**:
```json
{
    "url": "https://www.youtube.com/watch?v=video_id",
    "format": "mp4",  // opcional, padrão: "mp4"
    "quality": "best" // opcional, padrão: "best"
}
```

**Resposta (200)**:
```json
{
    "message": "Download iniciado",
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Verificar Status do Download
```http
GET /api/status/{task_id}
```

Verifica o status de um download em andamento.

**Resposta (200)**:
```json
{
    "status": "downloading",
    "progress": 45.5,
    "speed": 1048576,
    "eta": 120
}
```

### Cancelar Download
```http
POST /api/cancel/{task_id}
```

Cancela um download em andamento.

**Resposta (200)**:
```json
{
    "message": "Download cancelado"
}
```

## Informações de Vídeos

### Obter Informações do Vídeo
```http
GET /api/info/{video_id}
```

Retorna informações detalhadas sobre um vídeo.

**Resposta (200)**:
```json
{
    "title": "Nome do Vídeo",
    "duration": 180,
    "view_count": 1000000,
    "description": "Descrição do vídeo",
    "thumbnail": "URL da thumbnail",
    "formats": [
        {
            "format_id": "22",
            "ext": "mp4",
            "resolution": "720p",
            "filesize": 1048576
        }
    ]
}
```

### Listar Formatos Disponíveis
```http
GET /api/formats/{video_id}
```

Lista todos os formatos disponíveis para download.

**Resposta (200)**:
```json
[
    {
        "format_id": "22",
        "ext": "mp4",
        "resolution": "720p",
        "format_note": "HD"
    }
]
```

## Análise de Canais

### Informações do Canal
```http
GET /api/analytics/channel/info
```

Obtém informações detalhadas sobre um canal.

**Parâmetros Query**:
- `url`: URL do canal do YouTube

**Resposta (200)**:
```json
{
    "id": "channel_id",
    "name": "Nome do Canal",
    "description": "Descrição do canal",
    "subscriber_count": 1000000,
    "video_count": 500,
    "view_count": 50000000,
    "country": "BR",
    "joined_date": "20200101"
}
```

### Listar Vídeos do Canal
```http
GET /api/analytics/channel/videos
```

Obtém lista de vídeos de um canal.

**Parâmetros Query**:
- `url`: URL do canal do YouTube
- `limit`: Número máximo de vídeos (opcional, padrão: 50)

**Resposta (200)**:
```json
[
    {
        "id": "video_id",
        "title": "Título do Vídeo",
        "view_count": 10000,
        "like_count": 1000,
        "comment_count": 500,
        "upload_date": "20230801"
    }
]
```

### Estatísticas do Canal
```http
GET /api/analytics/channel/statistics
```

Obtém estatísticas gerais do canal.

**Parâmetros Query**:
- `url`: URL do canal do YouTube

**Resposta (200)**:
```json
{
    "video_metrics": {
        "total_videos_analyzed": 30,
        "average_views": 50000,
        "average_likes": 5000,
        "average_comments": 1000,
        "engagement_rate": 0.12
    },
    "upload_frequency": {
        "average_days_between_uploads": 3.5,
        "most_active_month": "2023-08",
        "total_uploads_analyzed": 30
    },
    "best_performing_video": {
        "id": "video_id",
        "title": "Título do Vídeo",
        "view_count": 100000
    }
}
```

### Análise de Desempenho
```http
GET /api/analytics/channel/performance
```

Obtém análise de desempenho do canal.

**Parâmetros Query**:
- `url`: URL do canal do YouTube

**Resposta (200)**:
```json
{
    "recent_performance": {
        "recent_videos_avg_views": 60000,
        "older_videos_avg_views": 40000,
        "growth_rate": 50.0,
        "trending_topics": [
            ["python", 10],
            ["tutorial", 8]
        ]
    },
    "upload_frequency": {
        "average_days_between_uploads": 3.5
    },
    "engagement_metrics": {
        "average_likes": 5000,
        "average_comments": 1000
    }
}
```

## Métricas de Vídeos

### Métricas Detalhadas
```http
GET /api/analytics/video/metrics/{video_id}
```

Obtém métricas detalhadas de um vídeo específico.

**Resposta (200)**:
```json
{
    "basic_info": {
        "title": "Título do Vídeo",
        "channel": "Nome do Canal",
        "duration": 600,
        "upload_date": "20230801"
    },
    "engagement": {
        "view_count": 50000,
        "like_count": 5000,
        "comment_count": 1000,
        "average_rating": 4.8
    },
    "technical": {
        "formats": 10,
        "available_qualities": ["720p", "1080p"],
        "filesize_approx": 104857600
    },
    "metadata": {
        "categories": ["Education"],
        "tags": ["python", "tutorial"],
        "language": "pt",
        "age_restricted": false
    }
}
```

## Códigos de Erro

A API pode retornar os seguintes códigos de erro:

- `400 Bad Request`: Parâmetros inválidos ou ausentes
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro interno do servidor

Exemplo de resposta de erro:
```json
{
    "error": "Mensagem de erro detalhada"
}
```

## Notas de Uso

1. Todas as URLs devem ser codificadas antes de serem enviadas como parâmetros
2. Os IDs de vídeo podem ser extraídos da URL do YouTube (ex: watch?v=VIDEO_ID)
3. O formato de data usado é YYYYMMDD
4. Tamanhos de arquivo são retornados em bytes
5. As durações são retornadas em segundos
