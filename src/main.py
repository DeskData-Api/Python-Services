# from database import Database
# from parser import parse_tickets
# from parser_simplificado import parse_tickets_simplificados
# import os

# def main():
#     # Inicializa o banco de dados
#     db = Database()
#     Database.wait_for_db(db.conn_params)
#     db.initialize()


#     # Processa os chamados
#     file_path = os.path.join("data", "chamados.csv")
#     chamados = parse_tickets(os.path.abspath(file_path))

#     # Insere os chamados no banco
#     success_count = 0
#     for chamado in chamados:
#         if db.insert_ticket(chamado):
#             success_count += 1
#         print(f"Processado chamado ID: {chamado['id']}")

#     print(f"\nProcessamento concluído!")
#     print(f"Total de chamados: {len(chamados)}")
#     print(f"Inseridos com sucesso: {success_count}")
#     print(f"Falhas: {len(chamados) - success_count}")

#     file_path = os.path.join("data", "tickets_simplificados.csv")
#     chamados = parse_tickets_simplificados(os.path.abspath(file_path))

#     success_count = 0
#     for chamado in chamados:
#         if db.insert_ticket_simplificado(chamado):
#             success_count += 1
#         print(f"Processado chamado ID: {chamado['id_da_item']}")
    
#     print(f"\nProcessamento concluído!")
#     print(f"Total de chamados: {len(chamados)}")
#     print(f"Inseridos com sucesso: {success_count}")
#     print(f"Falhas: {len(chamados) - success_count}")

# if __name__ == "__main__":
#     main()

import os
import argparse
from flask import Flask, request, jsonify
from database import Database
from parser import parse_tickets
from parser_simplificado import parse_tickets_simplificados

# ------------------------------------------------------------------ #
#  Configurações gerais
# ------------------------------------------------------------------ #
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ------------------------------------------------------------------ #
#  Instância única do banco
# ------------------------------------------------------------------ #
db = Database()
Database.wait_for_db(db.conn_params)
db.initialize()

# ------------------------------------------------------------------ #
#  Função que reproduz seu main() original
# ------------------------------------------------------------------ #
def process_csv_files() -> None:
    # ------------------- chamados.csv ------------------- #
    path = os.path.join(DATA_DIR, "chamados.csv")
    if os.path.exists(path):
        chamados = parse_tickets(path)
        sucesso = sum(1 for c in chamados if db.insert_ticket(c))
        print(f"chamados.csv → {sucesso}/{len(chamados)} inseridos.")
    else:
        print("⚠️  chamados.csv não encontrado, pulando.")

    # --------- tickets_simplificados.csv ---------------- #
    path = os.path.join(DATA_DIR, "tickets_simplificados.csv")
    if os.path.exists(path):
        simpl = parse_tickets_simplificados(path)
        sucesso = sum(1 for c in simpl if db.insert_ticket_simplificado(c))
        print(f"tickets_simplificados.csv → {sucesso}/{len(simpl)} inseridos.")
    else:
        print("⚠️  tickets_simplificados.csv não encontrado, pulando.")

# ------------------------------------------------------------------ #
#  Flask APP para upload
# ------------------------------------------------------------------ #
app = Flask(__name__)

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    """Salva o CSV recebido em /data e devolve mensagem de sucesso."""
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nome de arquivo vazio."}), 400
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Apenas arquivos .csv são permitidos."}), 400

    save_path = os.path.join(DATA_DIR, file.filename)
    file.save(save_path)

    return jsonify({"message": f"Arquivo {file.filename} salvo em /data."}), 200

# ------------------------------------------------------------------ #
#  Ponto de entrada
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Servidor de upload CSV + processamento em lote."
    )
    parser.add_argument(
        "--process",
        action="store_true",
        help="Processa os CSVs já existentes em /data e encerra.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3001,
        help="Porta do servidor Flask (padrão 3001).",
    )
    args = parser.parse_args()

    if args.process:
        process_csv_files()
    else:
        app.run(host="0.0.0.0", port=args.port, debug=True)