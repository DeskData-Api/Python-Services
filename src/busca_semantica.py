from fastapi import FastAPI, Query
from typing import List
import psycopg2
import os
import re
from fastapi.middleware.cors import CORSMiddleware

# Conexão com o banco
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "chamados_db")
DB_USER = os.getenv("DB_USER", "deskdata")
DB_PASS = os.getenv("DB_PASS", "deskdata")

app = FastAPI()

# CORS para permitir acesso pelo frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou restrinja para seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def conectar():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.get("/buscar")
def buscar_similares(q: str = Query(..., min_length=2)):
    conn = conectar()
    cursor = conn.cursor()

    termo = q.strip().lower()
    termo_sanitizado = re.sub(r"\s+", "", termo)

    consulta = """
        SELECT s.label, s.score,
               c1.id, c1.titulo, c1.descricao,
               c2.id, c2.titulo, c2.descricao
        FROM similaridade_chamados s
        JOIN chamados c1 ON c1.id = s.chamado_1
        JOIN chamados c2 ON c2.id = s.chamado_2
        WHERE REPLACE(LOWER(s.label), ' ', '') ILIKE %s
        ORDER BY s.score DESC
        LIMIT 10;
    """

    cursor.execute(consulta, (f"%{termo_sanitizado}%",))
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "label": row[0],
            "score": float(row[1]),
            "chamado_1": {
                "id": row[2],
                "titulo": row[3],
                "descricao": row[4],
            },
            "chamado_2": {
                "id": row[5],
                "titulo": row[6],
                "descricao": row[7],
            }
        }
        for row in resultados
    ]