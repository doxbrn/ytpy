#!/bin/bash

# Configurações
API_URL="http://localhost:5000/api"
VIDEO_ID="dQw4w9WgXcQ"  # Rick Roll para teste
FORMAT="mp4"
QUALITY="720p"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função para testar endpoint
test_endpoint() {
    local endpoint=$1
    local method=${2:-GET}
    local data=$3
    
    echo -e "\n${YELLOW}Testando $method $endpoint${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ Sucesso (HTTP $http_code)${NC}"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo -e "${RED}✗ Erro (HTTP $http_code)${NC}"
        echo "$body"
    fi
}

# Testa status da API
echo -e "\n${YELLOW}=== Testando Status da API ===${NC}"
test_endpoint "/status"

# Testa informações do vídeo
echo -e "\n${YELLOW}=== Testando Informações do Vídeo ===${NC}"
test_endpoint "/info?url=https://www.youtube.com/watch?v=$VIDEO_ID"

# Testa formatos disponíveis
echo -e "\n${YELLOW}=== Testando Formatos Disponíveis ===${NC}"
test_endpoint "/info/formats?url=https://www.youtube.com/watch?v=$VIDEO_ID"

# Testa legendas disponíveis
echo -e "\n${YELLOW}=== Testando Legendas Disponíveis ===${NC}"
test_endpoint "/subtitles?url=https://www.youtube.com/watch?v=$VIDEO_ID"

# Testa download do vídeo
echo -e "\n${YELLOW}=== Testando Download do Vídeo ===${NC}"
test_endpoint "/download" "POST" "{\"url\":\"https://www.youtube.com/watch?v=$VIDEO_ID\",\"format\":\"$FORMAT\",\"quality\":\"$QUALITY\"}"

# Testa progresso do download
echo -e "\n${YELLOW}=== Testando Progresso do Download ===${NC}"
test_endpoint "/download/progress/$VIDEO_ID"

# Testa análise do vídeo
echo -e "\n${YELLOW}=== Testando Análise do Vídeo ===${NC}"
test_endpoint "/analytics/video?url=https://www.youtube.com/watch?v=$VIDEO_ID"

# Testa análise do canal
echo -e "\n${YELLOW}=== Testando Análise do Canal ===${NC}"
test_endpoint "/analytics/channel?url=https://www.youtube.com/watch?v=$VIDEO_ID"

# Testa métricas
echo -e "\n${YELLOW}=== Testando Métricas ===${NC}"
test_endpoint "/metrics"

# Testa status do cache
echo -e "\n${YELLOW}=== Testando Status do Cache ===${NC}"
test_endpoint "/cache/status"

echo -e "\n${GREEN}Testes concluídos!${NC}"
