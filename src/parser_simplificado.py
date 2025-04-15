import pandas as pd
from datetime import datetime
import re
import json
import nltk
from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
import unidecode
import string

# Baixe uma vez:
# nltk.download('punkt')
# nltk.download('stopwords')

stopwords_pt = set(stopwords.words('portuguese'))
punct_translator = str.maketrans('', '', string.punctuation)
regex_color = re.compile(r'\{color:#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})\}|\{color\}|\{color:transparent\}')
regex_inline = re.compile(r'![^!]+!')
regex_links = re.compile(r'<[^>]+>')
regex_spaces = re.compile(r'\s+')

def preprocess_text(text):
    """Pré-processa texto com limpeza, acentuação, pontuação, stopwords e tokenização."""
    if not isinstance(text, str):
        return ""
    text = unidecode.unidecode(text.lower())
    text = text.translate(punct_translator)
    tokens = text.split()
    return ' '.join([t for t in tokens if t not in stopwords_pt])

def clean_space(value):
    if not isinstance(value, str):
        return ""

    value = value.strip()
    value = regex_color.sub('', value)
    value = regex_inline.sub('', value)
    value = regex_links.sub('', value)
    value = value.replace('|', '').replace('\n', ' ').replace('\\', ' ')
    value = regex_spaces.sub(' ', value)
    value = value.replace('nan', '').strip()

    if value.startswith('{adf}'):
        return preprocess_text(extract_text_from_adf(value))
    
    return preprocess_text(value)

def extract_text_from_adf(adf_content):
    """Extrai texto limpo de conteúdo ADF (formato JSON)."""
    try:
        if isinstance(adf_content, str):
            adf_content = adf_content.replace('{adf}', '')
            data = json.loads(adf_content)
        else:
            data = adf_content

        extracted_text = []

        def process_content(content):
            if not content:
                return
            for item in content:
                if "content" in item:
                    process_content(item["content"])
                if "text" in item:
                    text = item["text"].strip()
                    if text:
                        extracted_text.append(text)

        if "content" in data:
            process_content(data["content"])

        return ' '.join(extracted_text)

    except Exception as e:
        print(f"Erro ao processar o ADF: {e}")
        return ""

def parse_date(date_str):
    if not date_str or pd.isna(date_str) or date_str == '-':
        return None
    formats = ['%d/%b/%y %I:%M %p', '%Y-%m-%d %H:%M:%S.%f', '%d/%m/%y %H:%M']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def extract_attachments(row):
    """Extrai nomes dos anexos (sem links)."""
    anexo_cols = [col for col in row.index if col.startswith('Anexo')]
    anexos = [
        clean_text(row[col]).split('|')[0].strip()
        for col in anexo_cols if clean_text(row[col])
    ]
    return '; '.join(filter(None, anexos))

def clean_text(value):
    return preprocess_text(value) if isinstance(value, str) else ""

def process_ticket_row(row):
    """Processa uma linha do CSV para a tabela simplificada com PLN aplicado."""
    id_value = row['ID da item']
    if pd.isna(id_value) or id_value == '-':
        raise ValueError(f"ID inválido na linha: {row}")

    return {
        'id_da_item': int(id_value),
        'resumo': clean_text(row['Resumo']),
        'tipo': clean_text(row['Tipo do ticket']),
        'status': clean_text(row['Status']),
        'nome_do_projeto': clean_text(row['Nome do projeto']),
        'responsavel': clean_text(row['Responsável']),
        'criado': parse_date(row['Criado']),
        'atualizado': parse_date(row['Atualizado(a)']),
        'resolvido': parse_date(row['Resolvido']),
        'descricao': clean_space(row['Descrição']),
        'anexos': extract_attachments(row)
    }

def parse_tickets_simplificados(file_path):
    """Lê e processa o arquivo CSV para a tabela simplificada."""
    try:
        df = pd.read_csv(file_path, sep=',', encoding='utf-8')
        chamados = []
        for index, row in df.iterrows():
            try:
                chamado = process_ticket_row(row)
                chamados.append(chamado)
            except ValueError as e:
                print(f"Erro na linha {index}: {e}")
                continue
        return chamados
    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")
        return []