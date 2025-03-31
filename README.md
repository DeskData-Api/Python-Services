# 🐍 DeskData Python Services

> **Descrição breve**: DeskData Python Services é o microsserviço responsável pelo processamento e tratamento de dados de atendimentos inteligentes, utilizando Python para manipular arquivos CSV e preparar dados para análise.

---

## 📌 Status do Projeto

✅ **Sprint 1 Concluída - 30/03/2025**

✔ Serviço de tratamento de dados implementado  
🔜 Próximos passos: integração de Processamento de Linguagem Natural (PLN) e análise de sentimentos (Sprint 2)

📅 **Ciclo da Sprint 1**: 10/03/2025 - 30/03/2025

---

## 🎨 Visão Geral

🔹 **O que é?**  
Este serviço processa grandes volumes de dados gerados por sistemas de atendimento, como chamados técnicos, transformando arquivos CSV em informações estruturadas para armazenamento no banco de dados PostgreSQL e posterior visualização no frontend.

🔹 **Para quem?**  
Desenvolvedores e analistas que precisam de um pipeline automatizado para tratar dados brutos de atendimentos inteligentes.

🔹 **Funcionalidades da Sprint 1:**  
✔ Leitura e tratamento de arquivos CSV (chamados e Jira)  
✔ Normalização, limpeza e padronização de dados  
✔ Armazenamento dos dados tratados no PostgreSQL  

🔹 **Próximos Recursos (Sprints Futuras):**  
- Processamento de Linguagem Natural (PLN)  
- Análise de sentimentos  
- Busca semântica e prompt  
- Sumarização automática de interações  

---

## 📂 Estrutura do Projeto

```
/python-services
├── src/                 # Código-fonte principal
│   ├── main.py          # Script principal de execução
├── data/                # Diretório para arquivos CSV (ex.: chamados.csv)
├── requirements.txt     # Dependências Python
├── docker-compose.yml   # Configuração do container PostgreSQL
```

---

## 🛠 Tecnologias Utilizadas

- 🐍 **Python 3.8+** (Linguagem principal)  
- 📊 **Pandas** (Manipulação de dados)  
- 🐳 **Docker** + **Docker Compose** (Containerização do PostgreSQL)  
- 🗄️ **PostgreSQL** (Banco de dados)  

---

## 🚀 Como Rodar o Projeto

### 🔧 **Pré-requisitos**  
- [Python 3.8+](https://www.python.org/downloads/)  
- [Docker](https://www.docker.com/get-started) e [Docker Compose](https://docs.docker.com/compose/install/)  
- Arquivo CSV de chamados no formato especificado (colocar em `data/chamados.csv`)  
- [Git](https://git-scm.com/)

### 🛠 **Passos de Instalação**

1️⃣ **Clone o repositório**  
```bash
git clone https://github.com/DeskData-Api/Python-Services.git
cd python-services
```

2️⃣ **Crie e ative um ambiente virtual**  
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3️⃣ **Instale as dependências**  
```bash
pip install -r requirements.txt
```

4️⃣ **Prepare o arquivo CSV**  
Coloque o arquivo de chamados em `data/chamados.csv`. Certifique-se de que ele segue o formato esperado (ex.: colunas como `id`, `titulo`, `data_abertura`, etc., conforme documentado em "Arquitetura do Sistema").

5️⃣ **Inicie o container PostgreSQL**  
```bash
docker-compose up -d
```
Verifique se o banco está rodando em `localhost:5432` com as credenciais padrão (`deskdata:deskdata`).

6️⃣ **Execute o script principal**  
```bash
python src/main.py
```
O script processará o CSV e armazenará os dados no banco.

7️⃣ **Parando o container**  
```bash
docker-compose down
```

---

## 📝 Contribuindo

1. Faça um fork do repositório.  
2. Crie uma branch (`feature/nova-funcionalidade`).  
3. Commit suas alterações (`git commit -m 'feat: adiciona nova funcionalidade'`).  
4. Envie um Pull Request.

---

### 🎯 **Gostou do projeto?**

Se esse projeto foi útil para você, deixe uma ⭐ no repositório! 😃