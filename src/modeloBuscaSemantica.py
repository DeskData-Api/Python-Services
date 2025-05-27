import psycopg2
import os
from sentence_transformers import SentenceTransformer
import numpy as np

# Carrega o modelo de embeddings
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Conexão com o PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="chamados_db",
    user="deskdata",
    password="deskdata"
)
cursor = conn.cursor()

# Criação da tabela com array float8[]
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ticket_embeddings (
        id SERIAL PRIMARY KEY,
        chamado_id INT UNIQUE,
        titulo TEXT,
        descricao TEXT,
        embedding FLOAT8[]
    );
""")

# Busca os chamados (ajuste o nome da tabela e colunas conforme necessário)
cursor.execute("SELECT id, titulo, descricao FROM chamados;")
chamados = cursor.fetchall()

# Gera e salva os embeddings
for chamado_id, titulo, descricao in chamados:
    texto = f"{titulo} {descricao}"
    embedding = model.encode(texto).tolist()  # converte para list de float
    
    cursor.execute("""
        INSERT INTO ticket_embeddings (chamado_id, titulo, descricao, embedding)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (chamado_id) DO UPDATE SET embedding = EXCLUDED.embedding;
    """, (chamado_id, titulo, descricao, embedding))

conn.commit()
cursor.close()
conn.close()
print("Embeddings gerados e salvos com sucesso.")