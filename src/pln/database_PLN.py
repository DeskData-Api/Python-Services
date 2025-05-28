import psycopg2
import time
from psycopg2.extras import RealDictCursor
import json
import pandas as pd

def convert_timestamps(obj):
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, dict):
        # converte chave e valor
        return {
            str(convert_timestamps(k)): convert_timestamps(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [convert_timestamps(i) for i in obj]
    return obj


class Database_PLN:
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

    def wait_for_db(params, retries=5, delay=3):
        for i in range(retries):
            try:
                conn = psycopg2.connect(**params)
                conn.close()
                print("✅ Banco de dados disponível!")
                return
            except psycopg2.OperationalError as e:
                print(f"⏳ Tentativa {i+1} falhou: {e}")
                time.sleep(delay)
        raise Exception("❌ Não foi possível conectar ao banco de dados após várias tentativas.")
   
    def initialize(self):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    with open('src/pln/pln.sql', 'r') as f:
                        cur.execute(f.read())
            print("Banco de dados inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar o banco de dados: {e}")
        finally:
            conn.close()

    def get_all_tickets(self):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    query = "SELECT * FROM chamados;"
                    cur.execute(query)
                    return cur.fetchall()  # Retorna todos os dicionários
        except Exception as e:
            print(f"Erro ao buscar chamados: {e}")
            return []
        finally:
            conn.close()

    def count_tickets(self):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    query = "SELECT COUNT(id) FROM chamados;"
                    cur.execute(query)
                    result = cur.fetchone()
                    return result['count'] if result else 0
        except Exception as e:
            print(f"Erro ao contar chamados: {e}")
            return 0
        finally:
            conn.close()

    def insert_analise_pln(self, analise):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO analise_pln_chamados (
                            frequentes_problema,
                            agrupamento_categorias,
                            frequencia_categorias,
                            distribuicao_temporal
                        ) VALUES (
                            %(frequentes_problema)s,
                            %(agrupamento_categorias)s,
                            %(frequencia_categorias)s,
                            %(distribuicao_temporal)s
                        )
                    """
                    # Conversão segura dos dicts contendo datetime/timestamp
                    analise = {
                        **analise,
                        "frequentes_problema": json.dumps(convert_timestamps(analise.get("frequentes_problema", {}))),
                        "agrupamento_categorias": json.dumps(convert_timestamps(analise.get("agrupamento_categorias", {}))),
                        "frequencia_categorias": json.dumps(convert_timestamps(analise.get("frequencia_categorias", {}))),
                        "distribuicao_temporal": json.dumps(convert_timestamps(analise.get("distribuicao_temporal", {})))
                    }
                    cur.execute(query, analise)
            return True
        except Exception as e:
            print(f"Erro ao inserir análise de PLN: {e}")
            return False
        finally:
            conn.close()