import pytest
from fastapi.testclient import TestClient
from app.main import app, db, fila_prioridade


@pytest.fixture
def client():
    return TestClient(app)


def test_pagina_inicial(client):
    """Testa se a página HTML principal carrega com status 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Triage" in response.text
    assert "Manchester" in response.text


def test_analisar_sintomas(client):
    """Testa o endpoint de pré-visualização da IA."""
    payload = {
        "sintomas": "Dor no peito aguda com irradiação e sudorese fria",
        "idade": 58
    }
    response = client.post("/api/analisar-sintomas", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["cor"] in ["VERMELHO", "LARANJA"]
    assert data["score"] in [1, 2]
    assert "justificativa" in data


def test_fluxo_completo_triagem_e_chamada(client):
    """
    Testa o ciclo de vida completo:
    1. Cadastrar paciente e triagem via POST /api/triagem
    2. Verificar presença ordenada na fila via GET /api/fila
    3. Chamar paciente via POST /api/chamar-proximo
    4. Verificar histórico de atendimentos via GET /api/historico
    """
    # 1. Cadastro de paciente
    payload = {
        "nome": "Paciente Teste Automatizado",
        "cpf": "11122233344",
        "idade": 65,
        "eh_preferencial": True,
        "sintomas": "Dor no peito súbita com perda de consciência"
    }
    resp_triagem = client.post("/api/triagem", json=payload)
    assert resp_triagem.status_code == 201
    dados_triagem = resp_triagem.json()
    assert "item" in dados_triagem
    assert dados_triagem["item"]["nome"] == "Paciente Teste Automatizado"

    # 2. Consulta fila
    resp_fila = client.get("/api/fila")
    assert resp_fila.status_code == 200
    dados_fila = resp_fila.json()
    assert dados_fila["total"] >= 1

    # 3. Chamar próximo
    resp_chamada = client.post("/api/chamar-proximo", data={
        "medico_responsavel": "Dr. Sabatina",
        "observacoes": "Encaminhado para ECG"
    })
    assert resp_chamada.status_code == 200
    dados_chamada = resp_chamada.json()
    assert "paciente_chamado" in dados_chamada

    # 4. Histórico
    resp_historico = client.get("/api/historico")
    assert resp_historico.status_code == 200
    dados_historico = resp_historico.json()
    assert len(dados_historico["historico"]) >= 1
