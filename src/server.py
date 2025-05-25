from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as origens

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo vazio."}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Tipo de arquivo inválido."}), 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    return jsonify({"message": "Arquivo salvo com sucesso!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)