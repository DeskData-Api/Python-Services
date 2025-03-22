import pandas as pd
from datetime import datetime
import re 
def parse_date(date_str):
    """Converte string de data para datetime ou retorna None se inválida."""
    if not date_str or pd.isna(date_str) or date_str == '-':
        return None
    try:
        # Ajuste para diferentes formatos de data no documento
        formats = ['%d/%b/%y %I:%M %p', '%Y-%m-%d %H:%M:%S.%f', '%d/%m/%y %H:%M']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    except Exception:
        return None

def clean_text(value):
    """Limpa campos de texto, substituindo valores ausentes por string vazia."""
    if pd.isna(value) or value == '-' or value is None:
        return ""
    return str(value).strip()

def extract_attachments(row):
    """Extrai apenas os nomes dos anexos, ignorando links."""
    anexo_cols = [col for col in row.index if col.startswith('Anexo')]
    anexos = [clean_text(row[col]).split('|')[0].strip() if '|' in clean_text(row[col]) else clean_text(row[col]) 
              for col in anexo_cols if clean_text(row[col])]
    return '; '.join(filter(None, anexos))  # Junta os nomes com ponto e vírgula

def clean_space(value):
    value = str(value).strip()  # Remove espaços antes e depois

    # Remove marcações de cor {color:#XXXXXX} ou {color:#XXX}, onde X é um código hexadecimal
    value = re.sub(r'\{color:#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})\}', '', value)  # Remove {color:#fff} ou {color:#000000}
    value = re.sub(r'\{color\}', '', value)  # Remove {color} isolado

    # Remove marcações com !...! (como imagens ou links inline)
    value = re.sub(r'![^!]+!', '', value)

    # Remove links entre <[...]>
    value = re.sub(r'<[^>]+>', '', value)

    # Remove todas as quebras de linha e barras invertidas, unindo tudo em uma linha com espaços
    value = value.replace('\n', ' ').replace('\\', ' ').strip()

    # Remove espaços duplicados
    value = re.sub(r'\s+', ' ', value).strip()

    return value

def process_ticket_row(row):
    """Processa uma linha do CSV para a tabela simplificada."""
    id_value = row['ID da item']
    if pd.isna(id_value) or id_value == '-':
        raise ValueError(f"ID inválido na linha: {row}")

    return {
        'id_da_item': int(id_value),
        'resumo': clean_text(row['Resumo']),
        'tipo_do_ticket': clean_text(row['Tipo do ticket']),
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