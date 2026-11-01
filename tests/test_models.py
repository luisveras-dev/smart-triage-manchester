from datetime import datetime, timedelta

import pytest

from app.models import GrauRisco, Paciente, PacientePreferencial, Triagem


# ---------- Encapsulamento ----------
def test_idade_invalida_no_setter():
    p = Paciente("Ana", "111", 30)
    with pytest.raises(ValueError):
        p.idade = -1


def test_nome_vazio_no_setter():
    p = Paciente("Ana", "111", 30)
    with pytest.raises(ValueError):
        p.nome = "   "


def test_construtor_valida_idade():
    with pytest.raises(ValueError):
        Paciente("Ana", "111", -5)


# ---------- Herança ----------
def test_heranca():
    pref = PacientePreferencial("Bia", "222", 70)
    assert isinstance(pref, Paciente)
    assert pref.eh_preferencial is True
    assert Paciente("Ana", "111", 30).eh_preferencial is False


# ---------- Polimorfismo ----------
def test_polimorfismo_peso_desempate():
    pacientes = [Paciente("Ana", "111", 30), PacientePreferencial("Bia", "222", 70)]
    assert [p.peso_prioridade_desempate() for p in pacientes] == [1, 0]


def test_preferencial_vence_comum_na_mesma_cor():
    comum = Paciente("Ana", "111", 30)
    pref = PacientePreferencial("Bia", "222", 70)
    t = Triagem("febre", GrauRisco.AMARELO)
    assert pref.calcular_score_final(t) < comum.calcular_score_final(t)


def test_gravidade_vence_preferencia():
    comum = Paciente("Ana", "111", 30)
    pref = PacientePreferencial("Bia", "222", 70)
    grave = Triagem("parada", GrauRisco.VERMELHO)
    leve = Triagem("dor leve", GrauRisco.VERDE)
    assert comum.calcular_score_final(grave) < pref.calcular_score_final(leve)


def test_desempate_por_chegada():
    p1, p2 = Paciente("Ana", "111", 30), Paciente("Caio", "333", 25)
    agora = datetime.now()
    t1 = Triagem("dor", GrauRisco.VERDE, criado_em=agora)
    t2 = Triagem("dor", GrauRisco.VERDE, criado_em=agora + timedelta(minutes=5))
    assert p1.calcular_score_final(t1) < p2.calcular_score_final(t2)


# ---------- Enum ----------
def test_grau_risco_por_nome_e_score():
    assert GrauRisco.por_nome("vermelho") is GrauRisco.VERMELHO
    assert GrauRisco.por_score(2) is GrauRisco.LARANJA
    assert GrauRisco.por_score(99) is GrauRisco.AZUL