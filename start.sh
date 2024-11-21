#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Iniciando servidor YouTube Downloader...${NC}"

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python3 não encontrado. Por favor, instale o Python 3.${NC}"
    exit 1
fi

# Verifica se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}pip3 não encontrado. Por favor, instale o pip3.${NC}"
    exit 1
fi

# Cria ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# Ativa o ambiente virtual
echo -e "${GREEN}Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Instala ou atualiza dependências
echo -e "${GREEN}Instalando/atualizando dependências...${NC}"
pip install -r requirements.txt

# Cria diretórios necessários
echo -e "${GREEN}Criando diretórios necessários...${NC}"
mkdir -p downloads logs cache

# Verifica se arquivo .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Arquivo .env não encontrado. Criando arquivo .env padrão...${NC}"
    cat > .env << EOL
SECRET_KEY=your_secret_key_here
DOWNLOAD_FOLDER=downloads
MAX_DOWNLOADS=5
DEBUG=True
CACHE_DIR=cache
LOG_DIR=logs
MAX_REQUESTS_PER_MINUTE=60
EOL
fi

# Inicia o servidor
echo -e "${GREEN}Iniciando servidor Flask na porta 5001...${NC}"
export FLASK_APP=app.py
export FLASK_ENV=development
python app.py --port 5001
