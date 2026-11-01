import pytest
import random
from datetime import datetime, timedelta
from app.models.paciente import Paciente, PacientePreferencial
from app.models.triagem import Triagem, GrauRisco
from app.core.priority_queue import PriorityQueue, ItemFila


# ======================================================================
# Testes de integração com o modelo (pacientes reais)
# ======================================================================
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


# ======================================================================
# Testes da estrutura (fila isolada, com paciente de mentira)
# O paciente falso só tem o que a fila consome: nome e peso de desempate.
# ======================================================================
BASE = datetime(2026, 10, 31, 8, 0, 0)


class PacienteFalso:
    """Paciente de mentira: nome e peso de desempate (0 = preferencial, 1 = comum)."""

    def __init__(self, nome: str, preferencial: bool = False):
        self.nome = nome
        self._preferencial = preferencial

    def peso_prioridade_desempate(self) -> int:
        return 0 if self._preferencial else 1

    def calcular_score_final(self, triagem: Triagem) -> tuple[int, int, float]:
        return (
            triagem.grau_risco.score,
            self.peso_prioridade_desempate(),
            triagem.criado_em.timestamp(),
        )


def criar(
    nome: str, grau: GrauRisco, preferencial: bool = False, minuto: int = 0
) -> ItemFila:
    """Cria um item da fila cujo paciente chegou ``minuto`` minutos após a base."""
    triagem = Triagem("sintomas", grau, criado_em=BASE + timedelta(minutes=minuto))
    return ItemFila(PacienteFalso(nome, preferencial), triagem)


def esvaziar(fila: PriorityQueue) -> list[str]:
    """Remove tudo e devolve os nomes na ordem de saída."""
    nomes = []
    while not fila.esta_vazia():
        nomes.append(fila.remover_mais_urgente().paciente.nome)
    return nomes


# ---------- Estado básico ----------
def test_fila_nova_esta_vazia():
    fila = PriorityQueue()
    assert fila.esta_vazia()
    assert fila.tamanho() == 0


def test_fila_vazia_devolve_none():
    fila = PriorityQueue()
    assert fila.obter_primeiro() is None
    assert fila.remover_mais_urgente() is None


def test_tamanho_acompanha_insercoes_e_remocoes():
    fila = PriorityQueue()
    fila.inserir(criar("a", GrauRisco.LARANJA))
    fila.inserir(criar("b", GrauRisco.VERMELHO))
    assert fila.tamanho() == 2
    fila.remover_mais_urgente()
    assert fila.tamanho() == 1
    fila.remover_mais_urgente()
    assert fila.esta_vazia()


def test_remover_o_unico_elemento_esvazia_a_fila():
    fila = PriorityQueue()
    fila.inserir(criar("unico", GrauRisco.AZUL))
    assert fila.remover_mais_urgente().paciente.nome == "unico"
    assert fila.esta_vazia()


# ---------- Ordem de atendimento ----------
def test_prioridade_chave_segue_os_tres_criterios():
    item = criar("Bia", GrauRisco.AMARELO, preferencial=True, minuto=3)
    esperado = (
        GrauRisco.AMARELO.score,
        0,
        (BASE + timedelta(minutes=3)).timestamp(),
    )
    assert item.prioridade_chave == esperado


def test_exemplo_da_explicacao():
    fila = PriorityQueue()
    fila.inserir(criar("Ana", GrauRisco.VERDE, minuto=1))
    fila.inserir(criar("Bia", GrauRisco.AMARELO, minuto=2))
    fila.inserir(criar("Caio", GrauRisco.VERMELHO, minuto=3))
    fila.inserir(criar("Davi", GrauRisco.AMARELO, minuto=4))
    assert esvaziar(fila) == ["Caio", "Bia", "Davi", "Ana"]


def test_desempate_final_e_ordem_de_chegada():
    fila = PriorityQueue()
    fila.inserir(criar("segundo", GrauRisco.AMARELO, minuto=10))
    fila.inserir(criar("primeiro", GrauRisco.AMARELO, minuto=2))
    fila.inserir(criar("terceiro", GrauRisco.AMARELO, minuto=30))
    assert esvaziar(fila) == ["primeiro", "segundo", "terceiro"]


def test_gravidade_vence_preferencial():
    fila = PriorityQueue()
    fila.inserir(criar("idoso azul", GrauRisco.AZUL, preferencial=True, minuto=0))
    fila.inserir(criar("jovem vermelho", GrauRisco.VERMELHO, minuto=9))
    assert esvaziar(fila) == ["jovem vermelho", "idoso azul"]


# ---------- Consultas que não alteram a fila ----------
def test_obter_primeiro_nao_remove():
    fila = PriorityQueue()
    fila.inserir(criar("verde", GrauRisco.VERDE))
    fila.inserir(criar("vermelho", GrauRisco.VERMELHO))
    assert fila.obter_primeiro().paciente.nome == "vermelho"
    assert fila.tamanho() == 2


def test_listar_elementos_ordenado_e_sem_alterar_a_fila():
    fila = PriorityQueue()
    fila.inserir(criar("verde", GrauRisco.VERDE, minuto=0))
    fila.inserir(criar("vermelho", GrauRisco.VERMELHO, minuto=1))
    fila.inserir(criar("amarelo", GrauRisco.AMARELO, minuto=2))
    listados = [item.paciente.nome for item in fila.listar_elementos()]
    assert listados == ["vermelho", "amarelo", "verde"]
    assert fila.tamanho() == 3
    assert esvaziar(fila) == listados


# ---------- Propriedades do heap ----------
def test_propriedade_do_heap_vale_apos_muitas_operacoes():
    """
    Validação da Invariante Estrutural do Min-Heap Binário:
    Garante que para todo nó na posição 'pos' (exceto a raiz), seu pai
    na posição '(pos - 1) // 2' possui prioridade menor ou igual (heap[(pos-1)//2] <= heap[pos]),
    assegurando a corretude assintótica O(log n) das operações de sift-up e sift-down.
    """
    sorteio = random.Random(42)
    graus = list(GrauRisco)
    fila = PriorityQueue()
    for i in range(200):
        fila.inserir(criar(f"p{i}", sorteio.choice(graus), sorteio.random() < 0.3, i))
        if i % 7 == 0:
            fila.remover_mais_urgente()
        # Todo pai deve ser menor ou igual aos seus filhos.
        heap = fila._heap
        for pos in range(1, len(heap)):
            assert heap[(pos - 1) // 2] <= heap[pos]


def test_ordem_de_saida_bate_com_ordenacao_normal():
    sorteio = random.Random(7)
    graus = list(GrauRisco)
    # Cada paciente chega em um minuto diferente, então não há empate total.
    itens = [
        criar(f"p{i}", sorteio.choice(graus), sorteio.random() < 0.3, i)
        for i in range(300)
    ]
    fila = PriorityQueue()
    for item in itens:
        fila.inserir(item)
    esperado = [item.paciente.nome for item in sorted(itens, key=lambda x: x.prioridade_chave)]
    saida = [fila.remover_mais_urgente().paciente.nome for _ in itens]
    assert saida == esperado
