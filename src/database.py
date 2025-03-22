import psycopg2
from psycopg2.extras import RealDictCursor

class Database:
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

    def insert_ticket(self, chamado):
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
                    cur.execute(query, chamado)
            return True
        except Exception as e:
            print(f"Erro ao inserir chamado: {e}")
            return False
        finally:
            conn.close()

    def insert_ticket_simplificado(self, chamado):
        conn = self.connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO chamados_simplificados (
                            id_da_item, resumo, tipo_do_ticket, status, nome_do_projeto,
                            responsavel, criado, atualizado, resolvido, descricao, anexos
                        ) VALUES (
                            %(id_da_item)s, %(resumo)s, %(tipo_do_ticket)s, %(status)s,
                            %(nome_do_projeto)s, %(responsavel)s, %(criado)s,
                            %(atualizado)s, %(resolvido)s, %(descricao)s, %(anexos)s
                        )
                    """
                    cur.execute(query, chamado)
            return True
        except Exception as e:
            print(f"Erro ao inserir chamado simplificado: {e}")
            return False
        finally:
            conn.close()