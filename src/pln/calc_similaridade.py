import os
import sys
import psycopg2
import pandas as pd
import unidecode
import string
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
from difflib import SequenceMatcher

# === Conexão com banco
conn = psycopg2.connect(
    host="localhost", database="chamados_db", user="deskdata", password="deskdata", port=5432
)

# Permitir importar o database.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import Database

# === Pré-processamento
def preprocess(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = unidecode.unidecode(text.lower())
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ' '.join(text.split())
    return text.strip()

# === Lê dados
df = pd.read_sql("SELECT id_da_item, resumo, descricao FROM chamados_simplificados", conn)
df['texto'] = (df['resumo'].fillna('') + ' ' + df['descricao'].fillna('')).apply(preprocess)

# === Embeddings
print("🔍 Carregando modelo BERT...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("🧠 Gerando embeddings...")
embeddings = model.encode(df['texto'].tolist(), convert_to_tensor=True)

# === Calculando similaridade
print("📊 Calculando similaridades...")
similaridade_matrix = util.cos_sim(embeddings, embeddings)

# === Filtro + processamento
top_resultados = []
vistos = set()
limite_inferior = 50.0
limite_superior = 85.0

for i in tqdm(range(len(df)), desc="🔗 Processando pares similares"):
    texto_i = df.iloc[i]['texto']
    id_i = df.iloc[i]['id_da_item']
    resumo_i = df.iloc[i]['resumo']

    for j in range(i + 1, len(df)):
        texto_j = df.iloc[j]['texto']
        id_j = df.iloc[j]['id_da_item']
        resumo_j = df.iloc[j]['resumo']

        # Impede textos iguais ou quase iguais (SequenceMatcher > 95%)
        seq_sim = SequenceMatcher(None, texto_i, texto_j).ratio()
        if seq_sim > 0.95:
            continue

        score = similaridade_matrix[i][j].item() * 100
        if not (limite_inferior <= score <= limite_superior):
            continue

        chave = tuple(sorted([resumo_i.strip(), resumo_j.strip()]))
        if chave in vistos:
            continue
        vistos.add(chave)

        top_resultados.append({
            'chamado_1': int(id_i),
            'chamado_2': int(id_j),
            'label': f"{resumo_i[:35]} ≈ {resumo_j[:35]}",
            'score': round(score, 2)
        })

# === Exportar CSV
pd.DataFrame(top_resultados).to_csv("saida_similaridades_contextual.csv", index=False)

# === Inserir no banco
db = Database()
db.insert_similaridades(top_resultados)

print(f"✅ {len(top_resultados)} pares similares processados e salvos.")
