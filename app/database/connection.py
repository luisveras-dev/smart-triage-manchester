import sqlite3
import os
from typing import List, Optional, Dict, Any
from pathlib import Path


DB_PATH = os.environ.get("DATABASE_PATH", str(Path(__file__).parent.parent.parent / "hospital.db"))
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class DatabaseManager:
    """
    Gerenciador de Conexão e Repositório CRUD SQLite.
    Garante inicialização automática de tabelas e transações seguras.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._inicializar_banco()

    def _obter_conexao(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _inicializar_banco(self) -> None:
        """Cria as tabelas caso o banco ainda não exista."""
        if SCHEMA_PATH.exists():
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with self._obter_conexao() as conn:
                conn.executescript(schema_sql)

    # --- CRUD: Pacientes ---
    def salvar_paciente(self, nome: str, cpf: str, idade: int, eh_preferencial: bool) -> int:
        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            # Tenta buscar se o paciente já existe pelo CPF
            cursor.execute("SELECT id FROM pacientes WHERE cpf = ?", (cpf,))
            row = cursor.fetchone()
            if row:
                paciente_id = row["id"]
                cursor.execute(
                    "UPDATE pacientes SET nome = ?, idade = ?, eh_preferencial = ? WHERE id = ?",
                    (nome, idade, 1 if eh_preferencial else 0, paciente_id)
                )
                return paciente_id

            cursor.execute(
                """
                INSERT INTO pacientes (nome, cpf, idade, eh_preferencial)
                VALUES (?, ?, ?, ?)
                """,
                (nome, cpf, idade, 1 if eh_preferencial else 0)
            )
            return cursor.lastrowid

    def obter_paciente_por_id(self, paciente_id: int) -> Optional[Dict[str, Any]]:
        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # --- CRUD: Triagens ---
    def salvar_triagem(
        self,
        paciente_id: int,
        sintomas: str,
        gravidade_score: int,
        cor_manchester: str,
        tempo_maximo_minutos: int,
        justificativa_ia: str
    ) -> int:
        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO triagens (
                    paciente_id, sintomas, gravidade_score, cor_manchester,
                    tempo_maximo_minutos, justificativa_ia, status
                ) VALUES (?, ?, ?, ?, ?, ?, 'AGUARDANDO')
                """,
                (paciente_id, sintomas, gravidade_score, cor_manchester, tempo_maximo_minutos, justificativa_ia)
            )
            return cursor.lastrowid

    def atualizar_status_triagem(self, triagem_id: int, novo_status: str) -> None:
        with self._obter_conexao() as conn:
            conn.execute(
                "UPDATE triagens SET status = ? WHERE id = ?",
                (novo_status.upper(), triagem_id)
            )

    # --- CRUD: Atendimentos ---
    def registrar_atendimento(self, triagem_id: int, medico_responsavel: str, observacoes: str = "") -> int:
        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO atendimentos (triagem_id, medico_responsavel, observacoes)
                VALUES (?, ?, ?)
                """,
                (triagem_id, medico_responsavel, observacoes)
            )
            atendimento_id = cursor.lastrowid
            cursor.execute("UPDATE triagens SET status = 'ATENDIDO' WHERE id = ?", (triagem_id,))
            return atendimento_id

    def listar_historico_atendimentos(self, limite: int = 50) -> List[Dict[str, Any]]:
        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    a.id as atendimento_id,
                    a.medico_responsavel,
                    a.data_hora_chamada,
                    a.observacoes,
                    t.id as triagem_id,
                    t.sintomas,
                    t.cor_manchester,
                    t.gravidade_score,
                    t.justificativa_ia,
                    p.id as paciente_id,
                    p.nome as paciente_nome,
                    p.cpf as paciente_cpf,
                    p.idade as paciente_idade,
                    p.eh_preferencial
                FROM atendimentos a
                JOIN triagens t ON a.triagem_id = t.id
                JOIN pacientes p ON t.paciente_id = p.id
                ORDER BY a.data_hora_chamada DESC
                LIMIT ?
                """,
                (limite,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def listar_triagens_ativas(self) -> List[Dict[str, Any]]:
        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    t.id as triagem_id,
                    t.sintomas,
                    t.gravidade_score,
                    t.cor_manchester,
                    t.tempo_maximo_minutos,
                    t.justificativa_ia,
                    t.status,
                    t.criado_em as triagem_criado_em,
                    p.id as paciente_id,
                    p.nome as paciente_nome,
                    p.cpf as paciente_cpf,
                    p.idade as paciente_idade,
                    p.eh_preferencial
                FROM triagens t
                JOIN pacientes p ON t.paciente_id = p.id
                WHERE t.status = 'AGUARDANDO'
                ORDER BY t.criado_em ASC
                """
            )
            return [dict(row) for row in cursor.fetchall()]
