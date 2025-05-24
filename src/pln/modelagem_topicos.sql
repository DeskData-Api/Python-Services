

DROP TABLE IF EXISTS topics;

DROP TABLE IF EXISTS ticket_topics;


-- Quais palavras definem cada tópico
CREATE TABLE topics (
    topic_id      SERIAL PRIMARY KEY,
    top_terms     TEXT[],         -- ex.: '{senha,bloqueio,acesso}'
    term_weights  REAL[]          -- pesos na mesma ordem
);


-- Proporção de tópicos por ticket
CREATE TABLE ticket_topics (
    ticket_id     BIGINT  NOT NULL,
    topic_id      INT     NOT NULL REFERENCES topics(topic_id),
    proportion    REAL    NOT NULL,
    PRIMARY KEY (ticket_id, topic_id)
);