-- Schema do Banco de Dados SQLite do Sistema Hospitalar Smart Triage
-- Suporte a integridade referencial com FOREIGN KEYS

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    idade INTEGER NOT NULL,
    eh_preferencial BOOLEAN DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS triagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    sintomas TEXT NOT NULL,
    gravidade_score INTEGER NOT NULL,
    cor_manchester TEXT NOT NULL,
    tempo_maximo_minutos INTEGER NOT NULL,
    justificativa_ia TEXT,
    status TEXT DEFAULT 'AGUARDANDO',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS atendimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    triagem_id INTEGER NOT NULL,
    medico_responsavel TEXT NOT NULL,
    data_hora_chamada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT,
    FOREIGN KEY (triagem_id) REFERENCES triagens(id) ON DELETE CASCADE
);
