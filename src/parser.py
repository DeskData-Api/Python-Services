import pandas as pd
from datetime import datetime
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import unidecode
import string

# Baixar se necessário:
# nltk.download('punkt')
# nltk.download('stopwords')

stopwords_pt = set(stopwords.words('portuguese'))
regex_solicitante = re.compile(r'^.*?Solicitante:.*?\n', flags=re.IGNORECASE | re.DOTALL)
punct_translator = str.maketrans('', '', string.punctuation)

def preprocess_text(text):
    """Aplica pré-processamento completo a um texto."""
    if not isinstance(text, str):
        return ""

    #remoção de espaços, caixa baixa
    text = regex_solicitante.sub('', text).replace('\n', ' ').strip().lower()
    #remoção de acentuação
    text = unidecode.unidecode(text)
    #remoção de pontuação
    text = text.translate(punct_translator)
    #tokenização
    tokens = word_tokenize(text)
    #stopwords
    tokens = [t for t in tokens if t not in stopwords_pt]
    return ' '.join(tokens)

def parse_date(date_str):
    if not date_str or pd.isna(date_str):
        return None
    try:
        return datetime.strptime(date_str, '%d/%m/%Y %H:%M')
    except ValueError:
        return None

def parse_boolean(value):
    return value == 'Sim'

def process_ticket_row(row):
    return {
        'id': int(row['ID']),
        'titulo': preprocess_text(row['Título']),
        'entidade': preprocess_text(row['Entidade'].replace('ITO1 > ITO1_SD > ', '')),
        'categoria': preprocess_text(str(row['Categoria']).split('>')[-1]),
        'localizacao': preprocess_text(row['Localização']),
        'elementos_associados': preprocess_text(str(row['Elementos associados']).replace(" -", "")),
        'data_abertura': parse_date(row['Data de abertura']),
        'data_fechamento': parse_date(row['Data de fechamento']),
        'tempo_interno_excedido': parse_boolean(row['Tempo interno para atendimento excedido']),
        'tempo_resposta': parse_date(row['Tempo para atendimento']),
        'tempo_interno_resposta': parse_date(row['Tempo interno para atendimento']),
        'descricao': preprocess_text(row['Descrição']),
        'plugins': preprocess_text(row['Plug-ins - Tipo_Status - Status do Ticket']),
        'solucao': preprocess_text(row['Solução - Solução']),
        'status': preprocess_text(str(row['Status']).split(' ')[0]),
        'tipo': preprocess_text(row['Tipo']),
        'tecnico_atribuido': preprocess_text(row['Atribuído para - Técnico']),
        'fornecedor_atribuido': preprocess_text(row['Atribuído para - Atribuído a um fornecedor']),
        'ultima_atualizacao': parse_date(row['Última atualização'])
    }

def parse_tickets(file_path):
    df = pd.read_csv(file_path, sep=';', encoding='utf-8')
    return df.apply(process_ticket_row, axis=1).tolist()
