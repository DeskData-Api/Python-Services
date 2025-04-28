CREATE TABLE IF NOT EXISTS similaridade_chamados (
    id SERIAL PRIMARY KEY,
    chamado_1 INT,
    chamado_2 INT,
    label TEXT,
    score NUMERIC
);
