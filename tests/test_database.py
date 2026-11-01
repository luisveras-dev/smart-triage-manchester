import sqlite3

import pytest

from app.database.connection import DatabaseManager


@pytest.fixture
def db(tmp_path):
    """Cria um banco SQLite temporário e limpo para cada teste."""
    caminho = tmp_path / "teste.db"
    return DatabaseManager(db_path=str(caminho))


def _consultar(caminho, sql, params=()):
    """Consulta direta no arquivo .db, fora do DatabaseManager."""
    conn = sqlite3.connect(caminho)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def _criar_paciente_com_triagem(db, cpf="11122233344"):
    paciente_id = db.salvar_paciente("Maria Souza", cpf, 70, True)
    triagem_id = db.salvar_triagem(
        paciente_id, "dor no peito", 2, "LARANJA", 10, "Suspeita cardíaca"
    )
    return paciente_id, triagem_id


def test_banco_e_tabelas_sao_criados_automaticamente(tmp_path):
    caminho = tmp_path / "novo.db"
    assert not caminho.exists()

    DatabaseManager(db_path=str(caminho))

    assert caminho.exists()
    tabelas = {
        linha[0]
        for linha in _consultar(
            caminho, "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert {"pacientes", "triagens", "atendimentos"} <= tabelas


def test_salvar_e_obter_paciente(db):
    paciente_id = db.salvar_paciente("João Lima", "99988877766", 30, False)

    paciente = db.obter_paciente_por_id(paciente_id)

    assert paciente["nome"] == "João Lima"
    assert paciente["cpf"] == "99988877766"
    assert paciente["idade"] == 30
    assert paciente["eh_preferencial"] == 0


def test_obter_paciente_inexistente_retorna_none(db):
    assert db.obter_paciente_por_id(999) is None


def test_salvar_paciente_com_mesmo_cpf_atualiza_em_vez_de_duplicar(db):
    id_1 = db.salvar_paciente("Ana", "12345678900", 40, False)
    id_2 = db.salvar_paciente("Ana Maria", "12345678900", 41, True)

    assert id_1 == id_2
    paciente = db.obter_paciente_por_id(id_1)
    assert paciente["nome"] == "Ana Maria"
    assert paciente["idade"] == 41
    assert paciente["eh_preferencial"] == 1


def test_nova_triagem_nasce_aguardando_e_aparece_nas_ativas(db):
    paciente_id, triagem_id = _criar_paciente_com_triagem(db)

    ativas = db.listar_triagens_ativas()

    assert len(ativas) == 1
    assert ativas[0]["triagem_id"] == triagem_id
    assert ativas[0]["paciente_id"] == paciente_id
    assert ativas[0]["status"] == "AGUARDANDO"
    assert ativas[0]["cor_manchester"] == "LARANJA"


def test_atualizar_status_vira_maiusculo_e_sai_das_ativas(db):
    _, triagem_id = _criar_paciente_com_triagem(db)

    db.atualizar_status_triagem(triagem_id, "atendido")

    status = _consultar(
        db.db_path, "SELECT status FROM triagens WHERE id = ?", (triagem_id,)
    )[0][0]
    assert status == "ATENDIDO"
    assert db.listar_triagens_ativas() == []


def test_registrar_atendimento_marca_atendido_e_vai_para_historico(db):
    _, triagem_id = _criar_paciente_com_triagem(db)

    atendimento_id = db.registrar_atendimento(triagem_id, "Dr. Carlos", "Paciente estável")

    assert db.listar_triagens_ativas() == []
    historico = db.listar_historico_atendimentos()
    assert len(historico) == 1
    assert historico[0]["atendimento_id"] == atendimento_id
    assert historico[0]["medico_responsavel"] == "Dr. Carlos"
    assert historico[0]["paciente_nome"] == "Maria Souza"


def test_chave_estrangeira_impede_triagem_sem_paciente(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.salvar_triagem(999, "febre", 4, "VERDE", 120, "Quadro leve")


def test_falha_no_atendimento_nao_deixa_registro_pela_metade(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.registrar_atendimento(999, "Dr. Carlos")

    total = _consultar(db.db_path, "SELECT COUNT(*) FROM atendimentos")[0][0]
    assert total == 0

def test_rollback_desfaz_insercao_quando_segundo_passo_falha(db):
    _, triagem_id = _criar_paciente_com_triagem(db)

    conn = sqlite3.connect(db.db_path)
    conn.execute(
        "CREATE TRIGGER bloqueia_update BEFORE UPDATE ON triagens "
        "BEGIN SELECT RAISE(ABORT, 'falha simulada'); END;"
    )
    conn.commit()
    conn.close()

    with pytest.raises(sqlite3.DatabaseError):
        db.registrar_atendimento(triagem_id, "Dr. Carlos")

    total = _consultar(db.db_path, "SELECT COUNT(*) FROM atendimentos")[0][0]
    assert total == 0