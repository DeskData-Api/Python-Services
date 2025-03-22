from database import Database
from parser import parse_tickets
from parser_simplificado import parse_tickets_simplificados
import os

def main():
    # Inicializa o banco de dados
    db = Database()
    db.initialize()

    # # Processa os chamados
    # file_path = r'data\chamados.csv'
    # chamados = parse_tickets(os.path.abspath(file_path))

    # # Insere os chamados no banco
    # success_count = 0
    # for chamado in chamados:
    #     if db.insert_ticket(chamado):
    #         success_count += 1
    #     print(f"Processado chamado ID: {chamado['id']}")

    # print(f"\nProcessamento concluído!")
    # print(f"Total de chamados: {len(chamados)}")
    # print(f"Inseridos com sucesso: {success_count}")
    # print(f"Falhas: {len(chamados) - success_count}")

    file_path = r'data\tickets_simplificados.csv'
    chamados = parse_tickets_simplificados(os.path.abspath(file_path))

    success_count = 0
    for chamado in chamados:
        if db.insert_ticket_simplificado(chamado):
            success_count += 1
        print(f"Processado chamado ID: {chamado['id_da_item']}")
    
    print(f"\nProcessamento concluído!")
    print(f"Total de chamados: {len(chamados)}")
    print(f"Inseridos com sucesso: {success_count}")
    print(f"Falhas: {len(chamados) - success_count}")

if __name__ == "__main__":
    main()