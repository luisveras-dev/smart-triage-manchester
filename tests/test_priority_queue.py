import pytest
from datetime import datetime, timedelta
from app.models.paciente import Paciente, PacientePreferencial
from app.models.triagem import Triagem, GrauRisco
from app.core.priority_queue import PriorityQueue, ItemFila


def test_min_heap_ordenacao_gravidade():
    """
    Testa se o Min-Heap retira na ordem correta de Manchester:
    Vermelho (1) antes de Laranja (2) antes de Verde (4) antes de Azul (5).
    """
    heap = PriorityQueue()

    p_azul = Paciente("Paciente Azul", "111", 30)
    t_azul = Triagem("Dores crônicas", GrauRisco.AZUL)

    p_vermelho = Paciente("Paciente Vermelho", "222", 40)
    t_vermelho = Triagem("Parada respiratória", GrauRisco.VERMELHO)

    p_verde = Paciente("Paciente Verde", "333", 20)
    t_verde = Triagem("Arranhão", GrauRisco.VERDE)

    p_laranja = Paciente("Paciente Laranja", "444", 50)
    t_laranja = Triagem("Fratura exposta", GrauRisco.LARANJA)

    # Inserção propositalmente fora de ordem
    heap.inserir(ItemFila(p_azul, t_azul))
    heap.inserir(ItemFila(p_verde, t_verde))
    heap.inserir(ItemFila(p_vermelho, t_vermelho))
    heap.inserir(ItemFila(p_laranja, t_laranja))

    assert heap.tamanho() == 4

    # Remoção sucessiva deve seguir a ordem de urgência (1 -> 2 -> 4 -> 5)
    r1 = heap.remover_mais_urgente()
    assert r1.triagem.grau_risco == GrauRisco.VERMELHO

    r2 = heap.remover_mais_urgente()
    assert r2.triagem.grau_risco == GrauRisco.LARANJA

    r3 = heap.remover_mais_urgente()
    assert r3.triagem.grau_risco == GrauRisco.VERDE

    r4 = heap.remover_mais_urgente()
    assert r4.triagem.grau_risco == GrauRisco.AZUL

    assert heap.esta_vazia() is True


def test_desempate_paciente_preferencial():
    """
    Dois pacientes com a mesma cor (Amarelo).
    O paciente preferencial (idoso/gestante) deve ter prioridade sobre o paciente geral.
    """
    heap = PriorityQueue()
    agora = datetime.now()

    p_geral = Paciente("Paciente Geral", "111", 30, criado_em=agora)
    t_geral = Triagem("Febre", GrauRisco.AMARELO, criado_em=agora)

    p_pref = PacientePreferencial("Idoso Preferencial", "222", 72, criado_em=agora + timedelta(seconds=1))
    t_pref = Triagem("Febre", GrauRisco.AMARELO, criado_em=agora + timedelta(seconds=1))

    # Geral chegou 1 segundo antes, mas Preferencial tem desempate prioritário por lei
    heap.inserir(ItemFila(p_geral, t_geral))
    heap.inserir(ItemFila(p_pref, t_pref))

    primeiro = heap.remover_mais_urgente()
    assert primeiro.paciente.eh_preferencial is True
    assert primeiro.paciente.nome == "Idoso Preferencial"
