from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Libera o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def buscar_tickets():
    conn = psycopg2.connect(
        host="localhost",
        database="chamados_db",
        user="deskdata",
        password="deskdata"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT chamado_id, titulo, descricao, embedding FROM ticket_embeddings;")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

@app.get("/search")
def buscar_semanticamente(q: str = Query(..., min_length=1)):

    consulta_embedding = model.encode(q).reshape(1, -1)
    tickets = buscar_tickets()

    resultados = []
    for chamado_id, titulo, descricao, embedding in tickets:
        if embedding is None:
            continue
        emb_array = np.array(embedding).reshape(1, -1)
        similarity = cosine_similarity(consulta_embedding, emb_array)[0][0]
        resultados.append({
            "chamado_id": chamado_id,
            "titulo": titulo,
            "descricao": descricao,
            "similaridade": float(similarity)
        })

    # Ordena por similaridade
    resultados_ordenados = sorted(resultados, key=lambda x: x["similaridade"], reverse=True)
    return resultados_ordenados[:10]