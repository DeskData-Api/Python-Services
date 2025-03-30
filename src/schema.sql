CREATE TABLE IF NOT EXISTS chamados (
    id INTEGER PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    entidade VARCHAR(255),
    categoria VARCHAR(255),
    localizacao VARCHAR(255),
    elementos_associados VARCHAR(255),
    data_abertura TIMESTAMP,
    data_fechamento TIMESTAMP,
    tempo_interno_excedido BOOLEAN,
    tempo_resposta TIMESTAMP,
    tempo_interno_resposta TIMESTAMP,
    descricao TEXT,
    plugins VARCHAR(255),
    solucao TEXT,
    status VARCHAR(100),
    tipo VARCHAR(100),
    tecnico_atribuido VARCHAR(255),
    fornecedor_atribuido VARCHAR(255),
    ultima_atualizacao TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chamados_status ON chamados(status);
CREATE INDEX IF NOT EXISTS idx_chamados_data_abertura ON chamados(data_abertura);

CREATE TABLE IF NOT EXISTS chamados_simplificados (
    id_da_item INTEGER PRIMARY KEY,
    resumo VARCHAR(255) NOT NULL,
    tipo VARCHAR(100),
    status VARCHAR(100),
    nome_do_projeto VARCHAR(255),
    responsavel VARCHAR(255),
    criado TIMESTAMP,
    atualizado TIMESTAMP,
    resolvido TIMESTAMP,
    descricao TEXT,
    anexos TEXT
);

CREATE INDEX IF NOT EXISTS idx_chamados_simplificados_status ON chamados_simplificados(status);
CREATE INDEX IF NOT EXISTS idx_chamados_simplificados_criado ON chamados_simplificados(criado);