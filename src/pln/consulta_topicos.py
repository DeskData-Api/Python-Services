import psycopg2
from psycopg2.extras import RealDictCursor

class TopicosPLN:
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

    def get_topicos(self):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM topicos_lda ORDER BY id DESC LIMIT 1;")
                    resultado = cur.fetchone()
                    return resultado
        except Exception as e:
            print(f"Erro ao buscar tópicos: {e}")
            return None
        finally:
            conn.close()

# Exemplo de uso:
if __name__ == "__main__":
    pln = TopicosPLN()
    topicos = pln.get_topicos()
    if topicos:
        for chave, lista in topicos.items():
            if chave != 'id':
                print(f"{chave}: {lista}")