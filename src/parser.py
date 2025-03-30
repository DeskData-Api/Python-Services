import pandas as pd
from datetime import datetime
import re

def parse_date(date_str):
    if not date_str or pd.isna(date_str):
        return None
    try:
        return datetime.strptime(date_str, '%d/%m/%Y %H:%M')
    except ValueError:
        return None

def clean_text(value):
    """Limpa campos de texto, substituindo valores ausentes por string vazia."""
    if pd.isna(value) or value == '-' or value is None:
        return ""
    return str(value).strip()

def clean_caracter(value):
    return str(value).replace(" -", "")

def clean_space(value):
    value = str(value).strip()  # Garante que não tem espaços antes/depois

    # Remove tudo desde o início até a primeira quebra de linha depois de "Solicitante:"
    value = re.sub(r'^.*?Solicitante:.*?\n', '', value, flags=re.IGNORECASE | re.DOTALL).strip()

    # Remove todas as quebras de linha restantes, unindo tudo em uma linha
    value = value.replace('\n', ' ').strip()

    return value

def parse_boolean(value):
    return value == 'Sim'

def entidade(value):
    return str(value).replace('ITO1 > ITO1_SD > ','')

def categoria(value):
    return str(value).split('>')[-1].strip()

def process_ticket_row(row):
    return {
        'id': int(row['ID']),
        'titulo': row['Título'],
        'entidade': entidade(row['Entidade']),
        'categoria': categoria(row['Categoria']),
        'localizacao': row['Localização'],
        'elementos_associados': clean_caracter(row['Elementos associados']),
        'data_abertura': parse_date(row['Data de abertura']),
        'data_fechamento': parse_date(row['Data de fechamento']),
        'tempo_interno_excedido': parse_boolean(row['Tempo interno para atendimento excedido']),
        'tempo_resposta': parse_date(row['Tempo para atendimento']),
        'tempo_interno_resposta': parse_date(row['Tempo interno para atendimento']),
        'descricao': clean_space(row['Descrição']),
        'plugins': row['Plug-ins - Tipo_Status - Status do Ticket'],
        'solucao': clean_text(row['Solução - Solução']),
        'status': str(row['Status']).split(' ')[0],
        'tipo': row['Tipo'],
        'tecnico_atribuido': clean_text(row['Atribuído para - Técnico']),
        'fornecedor_atribuido': clean_text(row['Atribuído para - Atribuído a um fornecedor']),
        'ultima_atualizacao': parse_date(row['Última atualização'])
    }

def parse_tickets(file_path):
    # Lê o CSV com separador ponto e vírgula
    df = pd.read_csv(file_path, sep=';', encoding='utf-8')
    
    # Processa cada linha
    chamados = []
    for _, row in df.iterrows():
        chamado = process_ticket_row(row)
        chamados.append(chamado)
    
    return chamados