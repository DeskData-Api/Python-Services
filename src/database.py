import psycopg2
import time
from psycopg2.extras import RealDictCursor
import json
import pandas as pd


def convert_timestamps(obj):
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {
            str(convert_timestamps(k)): convert_timestamps(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [convert_timestamps(i) for i in obj]
    return obj


class Database:
    def __init__(self):
        self.conn_params = {
            "host": "localhost",
            "database": "chamados_db",
            "user": "deskdata",
            "password": "deskdata",
            "port": "5432"
        }
        self.conn = None  # manter conexão ativa se desejado

    def connect(self):
        self.conn = psycopg2.connect(**self.conn_params, cursor_factory=RealDictCursor)
        return self.conn

    @staticmethod
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
                    with open('src/schema.sql', 'r') as f:
                        cur.execute(f.read())
            print("Banco de dados inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar o banco de dados: {e}")
        finally:
            conn.close()

    def insert_tickets(self, chamados):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO chamados (
                            id, titulo, entidade, categoria, localizacao, elementos_associados,
                            data_abertura, data_fechamento, tempo_interno_excedido, tempo_resposta,
                            tempo_interno_resposta, descricao, plugins, solucao, status,
                            tipo, tecnico_atribuido, fornecedor_atribuido, ultima_atualizacao
                        ) VALUES (
                            %(id)s, %(titulo)s, %(entidade)s, %(categoria)s, %(localizacao)s,
                            %(elementos_associados)s, %(data_abertura)s, %(data_fechamento)s,
                            %(tempo_interno_excedido)s, %(tempo_resposta)s,
                            %(tempo_interno_resposta)s, %(descricao)s, %(plugins)s,
                            %(solucao)s, %(status)s, %(tipo)s, %(tecnico_atribuido)s,
                            %(fornecedor_atribuido)s, %(ultima_atualizacao)s
                        )
                    """
                    cur.executemany(query, chamados)
            return True
        except Exception as e:
            print(f"Erro ao inserir chamados em lote: {e}")
            return False
        finally:
            conn.close()

    def insert_tickets_simplificados(self, chamados):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO chamados_simplificados (
                            id_da_item, resumo, tipo, status, nome_do_projeto,
                            responsavel, criado, atualizado, resolvido, descricao, anexos
                        ) VALUES (
                            %(id_da_item)s, %(resumo)s, %(tipo)s, %(status)s,
                            %(nome_do_projeto)s, %(responsavel)s, %(criado)s,
                            %(atualizado)s, %(resolvido)s, %(descricao)s, %(anexos)s
                        )
                    """
                    cur.executemany(query, chamados)
            return True
        except Exception as e:
            print(f"Erro ao inserir chamados simplificados em lote: {e}")
            return False
        finally:
            conn.close()

    def insert_similaridades(self, similaridades):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO similaridade_chamados (chamado_1, chamado_2, label, score)
                        VALUES (%s, %s, %s, %s)
                    """
                    params = [
                        (
                            int(item['chamado_1']),
                            int(item['chamado_2']),
                            str(item['label']),
                            float(item['score'])
                        )
                        for item in similaridades
                    ]
                    cur.executemany(query, params)
            print("✅ Inserção de similaridades concluída com sucesso.")
        except Exception as e:
            print(f"❌ Erro ao inserir similaridades: {e}")
        finally:
            conn.close()

    def get_all_tickets(self):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    query = "SELECT * FROM chamados;"
                    cur.execute(query)
                    return cur.fetchall()
        except Exception as e:
            print(f"Erro ao buscar chamados: {e}")
            return []
        finally:
            conn.close()

    def get_all_tickets_simplificados(self):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    query = "SELECT * FROM chamados_simplificados;"
                    cur.execute(query)
                    return cur.fetchall()
        except Exception as e:
            print(f"Erro ao buscar chamados simplificados: {e}")
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
                    analise = {
                        **analise,
                        "frequentes_problema": json.dumps(convert_timestamps(analise.get("frequentes_problema", {}))),
                        "agrupamento_categorias": json.dumps(convert_timestamps(analise.get("agrupamento_categorias", {}))),
                        "frequencia_categorias": json.dumps(convert_timestamps(analise.get("frequencia_categorias", {}))),
                        "distribuicao_temporal": json.dumps(convert_timestamps(analise.get("distribuicao_temporal", {})))
                    }
                    cur.execute(query, analise)
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao inserir análise de PLN: {e}")
            return False
        finally:
            conn.close()