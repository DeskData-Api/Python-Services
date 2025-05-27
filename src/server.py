from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)  # habilita CORS para todas as rotas

# ---------- configuração de conexão -----------------
DB_PARAMS = {
    "host": "localhost",
    "database": "chamados_db",
    "user": "deskdata",
    "password": "deskdata",
    "port": "5432"
}

def get_db_conn():
    return psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)

# ---------- rota de upload (já existente) -----------
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    f = request.files['file']
    if f.filename == '':
        return jsonify({"error": "Nome de arquivo vazio."}), 400
    if not f.filename.lower().endswith('.csv'):
        return jsonify({"error": "Arquivo precisa ser .csv"}), 400

    path = os.path.join(UPLOAD_FOLDER, f.filename)
    f.save(path)
    return jsonify({"message": "Arquivo salvo com sucesso!"}), 200

# ---------- NOVA rota: GET /topicos -----------------
@app.route('/topicos', methods=['GET'])
def listar_topicos():
    try:
        conn = get_db_conn()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT topicos
                    FROM topicos_lda
                    ORDER BY id DESC LIMIT 1
                """)
                row = cur.fetchone()
                if row is None:
                    return jsonify([]), 200

                raw = row["topicos"]          # já desserializado pelo psycopg2
                resposta = []

                # raw é uma lista de dicts como no exemplo acima
                if isinstance(raw, list):
                    for item in raw:
                        for k, palavras in item.items():
                            resposta.append({
                                "topico": k,
                                "palavras": palavras
                                # sem pesos
                            })

                return jsonify(resposta), 200

    except Exception as e:
        print("Erro /topicos:", e)
        return jsonify({"error": "Falha ao buscar tópicos"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# ----------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)