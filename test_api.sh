#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URL base da API
BASE_URL="http://localhost:5001/api"

# Função para testar uma rota
test_route() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "\n${YELLOW}Testando: ${description}${NC}"
    echo -e "Endpoint: ${method} ${endpoint}"
    
    if [ -n "$data" ]; then
        echo -e "Dados: ${data}"
    fi
    
    # Executa o curl com ou sem dados
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X ${method} "${BASE_URL}${endpoint}")
    else
        response=$(curl -s -w "\n%{http_code}" -X ${method} "${BASE_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "${data}")
    fi
    
    # Extrai o código HTTP da resposta
    http_code=$(echo "$response" | tail -n1)
    # Extrai o corpo da resposta
    body=$(echo "$response" | sed '$d')
    
    # Verifica se a requisição foi bem sucedida
    if [ $http_code -ge 200 ] && [ $http_code -lt 300 ]; then
        echo -e "${GREEN}✓ Sucesso (HTTP ${http_code})${NC}"
    else
        echo -e "${RED}✗ Falha (HTTP ${http_code})${NC}"
    fi
    
    echo "Resposta:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    echo "----------------------------------------"
}

# Video de exemplo do YouTube para testes
VIDEO_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

echo -e "${GREEN}Iniciando testes da API...${NC}"

# 1. Teste de informações do vídeo
test_route "GET" "/info?url=${VIDEO_URL}" "" "Obter informações do vídeo"

# 2. Teste de formatos disponíveis
test_route "GET" "/formats?url=${VIDEO_URL}" "" "Listar formatos disponíveis"

# 3. Teste de download de vídeo
download_data='{
    "url": "'"${VIDEO_URL}"'",
    "format": "mp4",
    "quality": "best"
}'
test_route "POST" "/download" "$download_data" "Iniciar download de vídeo"

# 4. Teste de status do download (usando um task_id de exemplo)
test_route "GET" "/status/example-task-id" "" "Verificar status do download"

# 5. Teste de cancelamento de download
test_route "POST" "/cancel/example-task-id" "" "Cancelar download"

# 6. Teste de análise do canal
CHANNEL_URL="https://www.youtube.com/c/GoogleDevelopers"
test_route "GET" "/analytics/channel/info?url=${CHANNEL_URL}" "" "Obter informações do canal"

# 7. Teste de métricas do vídeo
test_route "GET" "/analytics/video/metrics/${VIDEO_URL##*=}" "" "Obter métricas do vídeo"

echo -e "\n${GREEN}Testes concluídos!${NC}"
