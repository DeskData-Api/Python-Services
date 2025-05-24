-- Remove tabelas existentes (se houver)
DROP TABLE IF EXISTS analise_pln_chamados;
DROP TABLE IF EXISTS chamados_simplificados;
DROP TABLE IF EXISTS chamados;
DROP TABLE IF EXISTS similaridade_chamados;

-- Recria a tabela 'chamados'
CREATE TABLE chamados (
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

CREATE INDEX idx_chamados_status ON chamados(status);
CREATE INDEX idx_chamados_data_abertura ON chamados(data_abertura);

-- Recria a tabela 'chamados_simplificados'
CREATE TABLE chamados_simplificados (
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

CREATE INDEX idx_chamados_simplificados_status ON chamados_simplificados(status);
CREATE INDEX idx_chamados_simplificados_criado ON chamados_simplificados(criado);

-- Cria a nova estrutura da tabela com suporte a análises mais complexas
CREATE TABLE analise_pln_chamados (
    id SERIAL PRIMARY KEY,
    frequentes_problema JSONB,                    -- termos mais comuns em descrição
    frequentes_titulo JSONB,                     -- termos mais comuns em solução
    agrupamento_categorias JSONB,                  -- agrupamentos semânticos entre categorias
    frequencia_categorias JSONB,                   -- contagem de categorias
    distribuicao_temporal JSONB,                   -- volume de chamados por semana
    data_analise TIMESTAMP DEFAULT NOW(),           -- data da análise
    insights_temporais TEXT[]
);

CREATE TABLE similaridade_chamados (
    id SERIAL PRIMARY KEY,
    chamado_1 INT,
    chamado_2 INT,
    label TEXT,
    score NUMERIC,
    created_at TIMESTAMP DEFAULT NOW()
);