from database import Database
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import pandas as pd

class Dashboard:

    def main():
        def categoria(df):
            # 3. Categorias mais frequentes com agrupamento por similaridade
            categorias = df['categoria'].dropna().unique().tolist()
            model = SentenceTransformer('all-MiniLM-L6-v2')
            cat_embeddings = model.encode(categorias)
            sim_matrix = cosine_similarity(cat_embeddings)

            # Agrupa categorias similares (>0.8 de similaridade)
            agrupadas = {}
            for i, cat in enumerate(categorias):
                for j in range(i+1, len(categorias)):
                    if sim_matrix[i][j] > 0.8:
                        agrupadas.setdefault(cat, []).append(categorias[j])
            return agrupadas
        
        def problemas(df):
            # 1. Junta título + descrição para problemas
            df['texto_problema'] = df['titulo'].fillna('') + ' ' + df['descricao'].fillna('')

            palavras_para_ignorar = {"solicito", "identificado"}

            # Tokeniza, remove palavras ignoradas e conta frequências
            all_problemas = " ".join(df['texto_problema']).split()
            all_problemas = [word for word in all_problemas if word not in palavras_para_ignorar]

            frequent_words = Counter(all_problemas).most_common(10)

            frequent_problemas = [{"name": word, "qtd": freq} for word, freq in frequent_words]
            return frequent_problemas
        
        def frequencia_categoria(df):
            # Conversão da data
            df['data_abertura'] = pd.to_datetime(df['data_abertura'], errors='coerce')

            # Criar coluna de quinzena manualmente
            df['quinzena'] = df['data_abertura'].apply(
            lambda d: f"{d.month:02d}/{d.year} (1ª Quinzena)" if d.day <= 15 else f"{d.month:02d}/{d.year} (2ª Quinzena)"
            )
            
            quinzena_categoria = df.groupby(['quinzena', 'categoria']).size().unstack(fill_value=0)

            # Agora para cada quinzena, pegar a categoria mais citada
            top_categoria_quinzena = []

            for quinzena, categorias in quinzena_categoria.iterrows():
                if categorias.sum() == 0:
                    continue
                categoria_top = categorias.idxmax()
                total_top = categorias.max()
                top_categoria_quinzena.append({
                    "quinzena": quinzena,
                    "categoria": categoria_top,
                    "qtd": int(total_top)
                })

            return top_categoria_quinzena
        
        db = Database()
        Database.wait_for_db(db.conn_params)
        db.initialize()

        if db.count_tickets() != 0:
            chamados = db.get_all_tickets()
            df = pd.DataFrame(chamados)

            frequent_problemas = problemas(df)
            agrupadas = categoria(df)
            cat_freq = df['categoria'].value_counts().to_dict()
            distribuicao_temporal = frequencia_categoria(df)

            analise = {
                "frequentes_problema": frequent_problemas,
                "agrupamento_categorias": agrupadas,
                "frequencia_categorias": cat_freq,
                "distribuicao_temporal": distribuicao_temporal,
            }

            db.insert_analise_pln(analise)

