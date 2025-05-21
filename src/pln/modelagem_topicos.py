import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import json

class ModelagemTopicos:
    def __init__(self):
        self.conn_params = {
            "host": "localhost",
            "database": "chamados_db",
            "user": "deskdata",
            "password": "deskdata",
            "port": "5432"
        }

    def connect(self):
        return psycopg2.connect(**self.conn_params, cursor_factory=RealDictCursor)

    def get_descricoes(self):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, descricao FROM chamados WHERE descricao IS NOT NULL;")
                    return cur.fetchall()
        finally:
            conn.close()

    def salvar_topicos(self, topicos):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS topicos_lda (
                            id SERIAL PRIMARY KEY,
                            topicos JSONB
                        );
                    """)
                    cur.execute("""
                        INSERT INTO topicos_lda (topicos)
                        VALUES (%s)
                    """, [json.dumps(topicos)])
        finally:
            conn.close()

    def modelar(self, n_topicos=3):
        dados = self.get_descricoes()
        descricoes = [d["descricao"] for d in dados]

        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(descricoes)

        lda = LatentDirichletAllocation(n_components=n_topicos, max_iter=1000, random_state=0)
        lda.fit(X)

        vocab = vectorizer.get_feature_names_out()
        topicos = []

        for i, topic_weights in enumerate(lda.components_):
            top_tokens = sorted(
                zip(vocab, topic_weights),
                key=lambda x: -x[1]
            )[:10]
            topicos.append({
                f"topico_{i+1}": [token for token, _ in top_tokens]
            })

        self.salvar_topicos(topicos)
        print("✅ Tópicos salvos com sucesso!")
        for t in topicos:
            print(t)

# Executar o script
if __name__ == "__main__":
    modelador = ModelagemTopicos()
    modelador.modelar(n_topicos=3)