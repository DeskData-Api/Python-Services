# Python-Services
Repositório referente aos serviços do python, e toda a parte de PLN.

## Pré-requisitos
- Docker e Docker Compose
- Python 3.8+
- Arquivo de chamados em CSV no formato especificado

## Setup

1. Clone o repositório:
```bash
git clone <repository-url>
cd python-services

Instale as dependências Python:

pip install -r requirements.txt

Coloque seu arquivo de chamados em data/chamados.csv

Inicie o container PostgreSQL:

docker-compose up -d

Execute o script principal:

python src/main.py

Parando o Container

docker-compose down