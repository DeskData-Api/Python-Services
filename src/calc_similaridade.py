import os
import sys
import string
import unidecode
import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# === Ajustes de path para importar Database
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from database import Database

class Similaridade:

    def main(lim_inf=50.0, lim_sup=85.0, top_k=500):
        def preprocess(text: str) -> str:
            """Limpa e normaliza um texto para comparação de similaridade."""
            if not isinstance(text, str):
                return ""
            text = unidecode.unidecode(text.lower())
            text = text.translate(str.maketrans('', '', string.punctuation))
            return ' '.join(text.split()).strip()

        def carregar_chamados():
            """Carrega os chamados simplificados do banco de dados."""
            db = Database()
            dados = db.get_all_tickets_simplificados()
            df = pd.DataFrame(dados)
            if df.empty:
                print("⚠️ Nenhum chamado simplificado encontrado no banco.")
                return df
            df['texto'] = (df['resumo'].fillna('') + ' ' + df['descricao'].fillna('')).apply(preprocess)
            return df

        def calcular_similaridades(df, modelo, lim_inf=50.0, lim_sup=85.0, top_k=500):
            """Calcula similaridades entre chamados com FAISS e filtro por score."""
            textos = df['texto'].tolist()
            if not textos:
                print("❌ Nenhum texto disponível para gerar embeddings.")
                return []

            print(f"📊 Gerando embeddings (batch_size=128)...")
            embeddings = modelo.encode(textos, convert_to_numpy=True, batch_size=128, normalize_embeddings=True)

            if len(embeddings) == 0 or len(embeddings.shape) < 2:
                print(f"❌ Embeddings vazios ou inválidos: {embeddings.shape}")
                return []

            print(f"🗭 Indexando embeddings no FAISS (dim={embeddings.shape[1]})...")
            index = faiss.IndexFlatIP(embeddings.shape[1])
            index.add(embeddings)

            print(f"🔍 Buscando top_k={top_k} vizinhos mais próximos para cada item...")
            _, indices = index.search(embeddings, top_k + 1)

            resultados = []
            vistos = set()
            dados = df[['id_da_item', 'resumo']].values.tolist()

            for i, vizinhos in enumerate(tqdm(indices, desc="🔗 Processando pares")):
                id_i, resumo_i = dados[i]
                for j in vizinhos[1:]:  # ignora o próprio item
                    score = float(np.dot(embeddings[i], embeddings[j]) * 100)
                    if score < lim_inf or score > lim_sup:
                        continue

                    id_j, resumo_j = dados[j]
                    chave = tuple(sorted([resumo_i.strip(), resumo_j.strip()]))
                    if chave in vistos:
                        continue
                    vistos.add(chave)

                    resultados.append({
                        'chamado_1': int(id_i),
                        'chamado_2': int(id_j),
                        'label': f"{resumo_i[:35]} ≈ {resumo_j[:35]}",
                        'score': round(score, 2)
                    })

            return resultados

        print("🔍 Carregando dados do banco...")
        df = carregar_chamados()
        if df.empty:
            print("❌ Nenhum dado carregado. Abortando execução.")
            return

        print("🧐 Carregando modelo BERT...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        print("🧠 Calculando similaridades...")
        similaridades = calcular_similaridades(df, model, lim_inf, lim_sup, top_k)

        if not similaridades:
            print("⚠️ Nenhuma similaridade encontrada. Nada foi salvo.")
            return

        print(f"📏 Salvando {len(similaridades)} pares no CSV...")
        pd.DataFrame(similaridades).to_csv("saida_similaridades_contextual.csv", index=False)

        print("📥 Inserindo no banco de dados...")
        db = Database()
        db.insert_similaridades(similaridades)

        print(f"✅ {len(similaridades)} pares similares processados e salvos.")
