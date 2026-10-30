from datetime import datetime
from typing import List, Optional, Tuple, Any
from app.models.paciente import Paciente
from app.models.triagem import Triagem, GrauRisco


class ItemFila:
    """
    Representa uma entrada na Fila de Prioridade.
    Contém a chave de ordenação composta para o Min-Heap:
      1º: Score Manchester (1=Vermelho mais urgente até 5=Azul)
      2º: Preferência por Lei (0=Preferencial antes de 1=Comum)
      3º: Timestamp de Chegada (FIFO para mesma urgência e preferência)
    """
    def __init__(self, paciente: Paciente, triagem: Triagem):
        self.paciente = paciente
        self.triagem = triagem
        self.timestamp_entrada = triagem.criado_em.timestamp()

    @property
    def prioridade_chave(self) -> Tuple[int, int, float]:
        """
        Retorna a tupla de comparação do Min-Heap:
        (gravidade_score, peso_preferencial, timestamp)
        """
        return (
            self.triagem.grau_risco.score,
            self.paciente.peso_prioridade_desempate(),
            self.timestamp_entrada
        )

    def __lt__(self, outro: "ItemFila") -> bool:
        return self.prioridade_chave < outro.prioridade_chave

    def __le__(self, outro: "ItemFila") -> bool:
        return self.prioridade_chave <= outro.prioridade_chave

    def __gt__(self, outro: "ItemFila") -> bool:
        return self.prioridade_chave > outro.prioridade_chave

    def __ge__(self, outro: "ItemFila") -> bool:
        return self.prioridade_chave >= outro.prioridade_chave

    def __eq__(self, outro: object) -> bool:
        if not isinstance(outro, ItemFila):
            return False
        return self.prioridade_chave == outro.prioridade_chave

    def to_dict(self) -> dict:
        return {
            "triagem_id": self.triagem.id,
            "paciente_id": self.paciente.id,
            "nome": self.paciente.nome,
            "cpf": self.paciente.cpf,
            "idade": self.paciente.idade,
            "eh_preferencial": self.paciente.eh_preferencial,
            "tipo_atendimento": self.paciente.tipo_atendimento(),
            "sintomas": self.triagem.sintomas,
            "cor": self.triagem.grau_risco.cor,
            "score": self.triagem.grau_risco.score,
            "tempo_maximo_minutos": self.triagem.grau_risco.tempo_espera_min,
            "justificativa_ia": self.triagem.justificativa_ia,
            "status": self.triagem.status,
            "horario_chegada": self.triagem.criado_em.strftime("%H:%M:%S")
        }


class PriorityQueue:
    """
    Fila de Prioridade implementada com Min-Heap Binário manual.
    Garante inserção O(log n) e remoção da maior prioridade O(log n).
    """
    def __init__(self):
        self._heap: List[ItemFila] = []

    def esta_vazia(self) -> bool:
        return len(self._heap) == 0

    def tamanho(self) -> int:
        return len(self._heap)

    def _pai(self, indice: int) -> int:
        return (indice - 1) // 2

    def _filho_esquerdo(self, indice: int) -> int:
        return 2 * indice + 1

    def _filho_direito(self, indice: int) -> int:
        return 2 * indice + 2

    def _trocar(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    def _sift_up(self, indice: int) -> None:
        """
        Operação de Subida no Min-Heap: O(log n).
        Restaura a propriedade de Heap movendo o elemento para cima
        enquanto ele for menor (mais prioritário) que seu pai.
        """
        while indice > 0:
            pai = self._pai(indice)
            if self._heap[indice] < self._heap[pai]:
                self._trocar(indice, pai)
                indice = pai
            else:
                break

    def _sift_down(self, indice: int) -> None:
        """
        Operação de Descida no Min-Heap: O(log n).
        Restaura a propriedade de Heap movendo o elemento para baixo
        comparando com o menor de seus filhos.
        """
        tamanho = len(self._heap)
        while True:
            menor = indice
            esq = self._filho_esquerdo(indice)
            dir = self._filho_direito(indice)

            if esq < tamanho and self._heap[esq] < self._heap[menor]:
                menor = esq

            if dir < tamanho and self._heap[dir] < self._heap[menor]:
                menor = dir

            if menor != indice:
                self._trocar(indice, menor)
                indice = menor
            else:
                break

    def inserir(self, item: ItemFila) -> None:
        """
        Insere um novo elemento no fim do Heap e faz o sift-up.
        Complexidade: O(log n).
        """
        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)

    def obter_primeiro(self) -> Optional[ItemFila]:
        """
        Retorna o paciente de maior prioridade (raiz) sem remover.
        Complexidade: O(1).
        """
        if self.esta_vazia():
            return None
        return self._heap[0]

    def remover_mais_urgente(self) -> Optional[ItemFila]:
        """
        Remove e retorna a raiz do Heap (paciente com maior urgência).
        Move o último elemento para a raiz e executa sift-down.
        Complexidade: O(log n).
        """
        if self.esta_vazia():
            return None

        if len(self._heap) == 1:
            return self._heap.pop()

        raiz = self._heap[0]
        # Move o último para a raiz e remove do final O(1)
        self._heap[0] = self._heap.pop()
        self._sift_down(0)
        return raiz

    def listar_elementos(self) -> List[ItemFila]:
        """
        Retorna uma cópia da fila ordenada por prioridade (sem destruir a fila original).
        Usa extração ordenada em cópia do Heap.
        """
        copia_heap = PriorityQueue()
        # Clona elementos
        copia_heap._heap = list(self._heap)

        resultado = []
        while not copia_heap.esta_vazia():
            resultado.append(copia_heap.remover_mais_urgente())
        return resultado
