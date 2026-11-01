from unittest.mock import MagicMock
import pytest
from app.services.ai_service import AIService, CLINICAL_SYSTEM_PROMPT, MANCHESTER_SPECS


# ==============================================================================
# 1. Testes de Inicialização e Fallback Básico
# ==============================================================================

def test_ai_service_sem_chave_inicia_com_fallback():
    """Garante que sem chave de API o serviço inicializa com client=None."""
    service = AIService(api_key="")
    assert service.client is None

    resultado = service.classificar_sintomas("Dor no peito com sudorese fria")
    assert resultado["cor"] == "VERMELHO"
    assert resultado["score"] == 1
    assert resultado["tempo_maximo_minutos"] == 0
    assert "Fallback" in resultado["metodo"]


def test_ai_service_sintomas_vazios_retorna_azul():
    """Garante que queixas vazias ou nulas recebem classificação Azul sem erro."""
    service = AIService(api_key="")
    
    for entrada in ["", "   ", None]:
        resultado = service.classificar_sintomas(entrada)
        assert resultado["cor"] == "AZUL"
        assert resultado["score"] == 5
        assert resultado["tempo_maximo_minutos"] == 240


# ==============================================================================
# 2. Testes das 5 Categorias do Fallback Heurístico (Protocolo de Manchester)
# ==============================================================================

def test_fallback_classificacao_vermelho():
    """Casos de risco iminente de morte devem ser classificados como Vermelho."""
    service = AIService(api_key="")
    casos = [
        "Paciente inconsciente e não respira",
        "Dor no peito intensa com suspeita de infarto",
        "Parada cardiorrespiratória em curso",
        "Choque anafilático e asfixia",
        "Paciente em coma com cianose labial"
    ]
    for caso in casos:
        res = service.classificar_sintomas(caso)
        assert res["cor"] == "VERMELHO", f"Falhou para caso: {caso}"
        assert res["score"] == 1
        assert res["tempo_maximo_minutos"] == 0


def test_fallback_classificacao_laranja():
    """Casos muito urgentes devem ser classificados como Laranja."""
    service = AIService(api_key="")
    casos = [
        "Fratura exposta em perna esquerda com dor intensa",
        "Falta de ar moderada a severa e dispneia",
        "Suspeita de AVC com perda de força súbita no braço",
        "Cefaleia súbita e intensa com pressão 20",
        "Queimadura grave de segundo grau"
    ]
    for caso in casos:
        res = service.classificar_sintomas(caso)
        assert res["cor"] == "LARANJA", f"Falhou para caso: {caso}"
        assert res["score"] == 2
        assert res["tempo_maximo_minutos"] == 10


def test_fallback_classificacao_amarelo():
    """Casos urgentes devem ser classificados como Amarelo."""
    service = AIService(api_key="")
    casos = [
        "Febre alta persistente e dor de cabeça moderada",
        "Dor abdominal aguda com vômitos frequentes",
        "Diarreia aguda com desidratacao moderada",
        "Crise de asma leve e tosse persistente",
        "Dor moderada na região lombar suspeita de cólica renal"
    ]
    for caso in casos:
        res = service.classificar_sintomas(caso)
        assert res["cor"] == "AMARELO", f"Falhou para caso: {caso}"
        assert res["score"] == 3
        assert res["tempo_maximo_minutos"] == 60


def test_fallback_classificacao_verde():
    """Casos pouco urgentes devem ser classificados como Verde."""
    service = AIService(api_key="")
    casos = [
        "Resfriado com tosse leve e coriza há 3 dias",
        "Garganta inflamada sem febre",
        "Escoriação leve no joelho após queda",
        "Dor muscular leve após exercício",
        "Unha encravada sem sinais de infecção grave"
    ]
    for caso in casos:
        res = service.classificar_sintomas(caso)
        assert res["cor"] == "VERDE", f"Falhou para caso: {caso}"
        assert res["score"] == 4
        assert res["tempo_maximo_minutos"] == 120


def test_fallback_classificacao_azul():
    """Casos não urgentes ou queixas crônicas devem ser classificados como Azul."""
    service = AIService(api_key="")
    casos = [
        "Vim apenas pegar receita médica",
        "Retorno ambulatorial para checar exame",
        "Paciente para troca de curativo simples",
        "Dores articulares crônicas há 2 anos sem alteração recente"
    ]
    for caso in casos:
        res = service.classificar_sintomas(caso)
        assert res["cor"] == "AZUL", f"Falhou para caso: {caso}"
        assert res["score"] == 5
        assert res["tempo_maximo_minutos"] == 240


# ==============================================================================
# 3. Testes de Robustez Léxica (Acentuação, Caixa Alta e Pontuação)
# ==============================================================================

def test_fallback_normalizacao_acentos_e_caixa():
    """Garante que variações com acentos e maiúsculas funcionam igualmente."""
    service = AIService(api_key="")

    res_com_acento = service.classificar_sintomas("Paciente com convulsão e não respira")
    res_sem_acento = service.classificar_sintomas("Paciente com convulsao e nao respira")
    res_maiusculas = service.classificar_sintomas("PACIENTE COM CONVULSAO E NAO RESPIRA")

    assert res_com_acento["cor"] == "VERMELHO"
    assert res_sem_acento["cor"] == "VERMELHO"
    assert res_maiusculas["cor"] == "VERMELHO"


# ==============================================================================
# 4. Testes do Parser de Resposta JSON da IA
# ==============================================================================

def test_parser_json_puro():
    """Testa parsing de JSON limpo e estrito."""
    service = AIService(api_key="")
    json_str = '{"cor": "VERMELHO", "score": 1, "justificativa": "Suspeita de IAM", "tempo_maximo_minutos": 0}'
    resultado = service._parse_resposta_json(json_str)

    assert resultado["cor"] == "VERMELHO"
    assert resultado["score"] == 1
    assert resultado["tempo_maximo_minutos"] == 0
    assert resultado["justificativa"] == "Suspeita de IAM"
    assert "IA Generativa" in resultado["metodo"]


def test_parser_json_com_markdown_codeblocks():
    """Testa parsing quando a IA envolve a resposta em blocos de markdown ```json."""
    service = AIService(api_key="")
    resposta_markdown = """```json
{
  "cor": "LARANJA",
  "score": 2,
  "justificativa": "Dispneia severa e dor aguda.",
  "tempo_maximo_minutos": 10
}
```"""
    resultado = service._parse_resposta_json(resposta_markdown)

    assert resultado["cor"] == "LARANJA"
    assert resultado["score"] == 2
    assert resultado["tempo_maximo_minutos"] == 10
    assert resultado["justificativa"] == "Dispneia severa e dor aguda."


def test_parser_reconcilia_inconsistencias_com_protocolo():
    """Garante que se o modelo errar o score ou tempo de uma cor, o sistema corrige."""
    service = AIService(api_key="")
    # Score 99 e tempo 999 para cor AMARELO
    json_inconsistente = '{"cor": "AMARELO", "score": 99, "justificativa": "Febre", "tempo_maximo_minutos": 999}'
    resultado = service._parse_resposta_json(json_inconsistente)

    assert resultado["cor"] == "AMARELO"
    assert resultado["score"] == 3  # Corrigido para 3
    assert resultado["tempo_maximo_minutos"] == 60  # Corrigido para 60


def test_parser_json_invalido_lanca_erro():
    """Texto aleatório sem JSON ou com cor inexistente deve lançar ValueError."""
    service = AIService(api_key="")

    with pytest.raises(ValueError):
        service._parse_resposta_json("Texto sem nenhum JSON aqui.")

    with pytest.raises(ValueError):
        service._parse_resposta_json('{"cor": "ROSA", "score": 1}')


# ==============================================================================
# 5. Testes com Mock da API Google Gemini (Sucesso e Resiliência a Falhas)
# ==============================================================================

def test_classificar_com_gemini_sucesso():
    """Testa chamada bem sucedida à API do Gemini usando Mock."""
    service = AIService(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"cor": "LARANJA", "score": 2, "justificativa": "Suspeita de AVC em paciente idoso.", "tempo_maximo_minutos": 10}'
    mock_client.models.generate_content.return_value = mock_response

    service.client = mock_client

    resultado = service.classificar_sintomas("Perda súbita de força no braço direito", idade=68)

    assert resultado["cor"] == "LARANJA"
    assert resultado["score"] == 2
    assert resultado["tempo_maximo_minutos"] == 10
    assert "IA Generativa" in resultado["metodo"]
    assert mock_client.models.generate_content.called


def test_resiliencia_erro_conexao_api_ativa_fallback():
    """
    DoD: O sistema NUNCA quebra se a API falhar (ex: sem internet, chave inválida, erro 500).
    Deve acionar o fallback heurístico transparentemente.
    """
    service = AIService(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = ConnectionError("Sem conexão com a internet")
    service.client = mock_client

    # Não deve levantar exceção!
    resultado = service.classificar_sintomas("Dor no peito aguda e sudorese fria", idade=55)

    assert resultado["cor"] == "VERMELHO"
    assert resultado["score"] == 1
    assert "Fallback" in resultado["metodo"]


def test_resiliencia_resposta_invalida_da_ia_ativa_fallback():
    """
    DoD: Se a IA retornar texto alucinado ou que não seja JSON, o fallback deve assumir.
    """
    service = AIService(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Desculpe, como um modelo de IA eu não posso responder em JSON."
    mock_client.models.generate_content.return_value = mock_response
    service.client = mock_client

    resultado = service.classificar_sintomas("Febre alta e vômitos constantes", idade=25)

    assert resultado["cor"] == "AMARELO"
    assert resultado["score"] == 3
    assert "Fallback" in resultado["metodo"]


# ==============================================================================
# 6. Testes do System Prompt Clínico e Especificações Manchester
# ==============================================================================

def test_system_prompt_clinico_contem_regras_manchester():
    """Verifica se o prompt do sistema cobre todas as diretrizes exigidas."""
    for cor in ["VERMELHO", "LARANJA", "AMARELO", "VERDE", "AZUL"]:
        assert cor in CLINICAL_SYSTEM_PROMPT
    assert "JSON" in CLINICAL_SYSTEM_PROMPT
    assert "tempo_maximo_minutos" in CLINICAL_SYSTEM_PROMPT


def test_manchester_specs_completas():
    """Valida o dicionário canônico com as 5 cores e tempos máximos de Manchester."""
    assert len(MANCHESTER_SPECS) == 5
    assert MANCHESTER_SPECS["VERMELHO"]["score"] == 1
    assert MANCHESTER_SPECS["VERMELHO"]["tempo_maximo_minutos"] == 0
    assert MANCHESTER_SPECS["LARANJA"]["score"] == 2
    assert MANCHESTER_SPECS["LARANJA"]["tempo_maximo_minutos"] == 10
    assert MANCHESTER_SPECS["AMARELO"]["score"] == 3
    assert MANCHESTER_SPECS["AMARELO"]["tempo_maximo_minutos"] == 60
    assert MANCHESTER_SPECS["VERDE"]["score"] == 4
    assert MANCHESTER_SPECS["VERDE"]["tempo_maximo_minutos"] == 120
    assert MANCHESTER_SPECS["AZUL"]["score"] == 5
    assert MANCHESTER_SPECS["AZUL"]["tempo_maximo_minutos"] == 240
