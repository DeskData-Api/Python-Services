-- Remove tabela anterior, se existir
DROP TABLE IF EXISTS analise_pln_chamados;

-- Cria a nova estrutura da tabela com suporte a análises mais complexas
CREATE TABLE analise_pln_chamados (
    id SERIAL PRIMARY KEY,
    frequentes_problema JSONB,                    -- termos mais comuns em descrição
    agrupamento_categorias JSONB,                  -- agrupamentos semânticos entre categorias
    frequencia_categorias JSONB,                   -- contagem de categorias
    distribuicao_temporal JSONB,                   -- volume de chamados por semana
    data_analise TIMESTAMP DEFAULT NOW(),           -- data da análise
    insights_temporais TEXT[]
);
