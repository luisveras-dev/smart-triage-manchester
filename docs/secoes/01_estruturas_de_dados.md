# Pilar 1: Estruturas de Dados (Fila de Prioridade com Min-Heap)

**Responsável:** Integrante responsável por Estruturas de Dados  
**Arquivo principal no código:** `app/core/priority_queue.py`

---

## 1. Visão Geral da Implementação
No sistema hospitalar, o atendimento não segue ordem estrita de chegada (FIFO simples), mas sim o **Protocolo de Manchester** (gravidade clínica). No entanto, quando dois pacientes possuem a mesma gravidade, o critério de desempate por lei e por ordem de chegada deve ser respeitado.

Para atender a esse requisito com alta eficiência, foi implementada uma **Fila de Prioridade manual baseada em Min-Heap Binário** (`MinHeapPriorityQueue`), sem uso de bibliotecas prontas como `heapq`, demonstrando a manipulação direta da estrutura em array.

---

## 2. A Chave de Prioridade e o Desempate
Cada elemento na fila é encapsulado na classe `ItemFila`, cuja prioridade é definida por uma tupla comparativa de 3 níveis:

$$\text{prioridade\_chave} = (\text{gravidade\_score}, \text{peso\_preferencial}, \text{timestamp})$$

1. **`gravidade_score` (1 a 5):** 
   * `1` = Emergência (Vermelho) — maior prioridade no Min-Heap (menor número).
   * `2` = Muito Urgente (Laranja).
   * `3` = Urgente (Amarelo).
   * `4` = Pouco Urgente (Verde).
   * `5` = Não Urgente (Azul).
2. **`peso_preferencial` (0 ou 1):**
   * `0` = Preferencial por lei (idosos $\ge 60$ anos, gestantes, PcD).
   * `1` = Paciente comum.
3. **`timestamp` (float):**
   * Momento em que o paciente entrou na fila. Garante o critério **FIFO** para pacientes com mesma gravidade e preferência.

> Como a comparação de tuplas em Python avalia elemento por elemento da esquerda para a direita, um paciente Vermelho (`score=1`) sempre sairá antes de um Amarelo (`score=3`), independentemente do horário de chegada.

---

## 3. Análise de Complexidade Assintótica

| Operação | Método | Complexidade de Tempo | Justificativa Técnica |
| :--- | :--- | :---: | :--- |
| **Inserção** | `inserir(item)` | $\mathcal{O}(\log n)$ | Adiciona no final do array e executa `_sift_up` percorrendo a altura da árvore binária. |
| **Remoção do Topo** | `remover_proximo()` | $\mathcal{O}(\log n)$ | Substitui a raiz pelo último elemento e executa `_sift_down` reorganizando o heap até as folhas. |
| **Consulta (Peek)** | `proximo()` | $\mathcal{O}(1)$ | Acesso direto ao elemento de índice 0 do array (raiz do heap). |
| **Tamanho / Vazio** | `tamanho()`, `esta_vazia()` | $\mathcal{O}(1)$ | Consulta direta ao tamanho do array interno (`len(self._heap)`). |

### Por que não usar uma lista ordenada convencional?
* Em uma lista ordenada comum, a inserção custa $\mathcal{O}(n)$ devido ao deslocamento de elementos na memória.
* No Min-Heap, tanto a inserção quanto a remoção são garantidas em tempo logarítmico $\mathcal{O}(\log n)$, tornando a fila escalável mesmo com centenas de pacientes simultâneos.

---

## 4. Relações de Índices no Array
A árvore binária completa é mapeada diretamente em um vetor linear (`self._heap = []`):
* **Índice do Pai de $i$:** `(i - 1) // 2`
* **Filho Esquerdo de $i$:** `2 * i + 1`
* **Filho Direito de $i$:** `2 * i + 2`

---

## 5. Perguntas Frequentes para Apresentação

### Q1: O que acontece se chegarem dois pacientes Vermelhos ao mesmo tempo?
**R:** A tupla compara o primeiro critério (`1 == 1`). Em seguida, verifica o peso preferencial. Se ambos forem preferenciais (ou ambos comuns), o desempate ocorre no terceiro elemento da tupla: o `timestamp` de entrada. Quem chegou milissegundos antes terá um número menor e, portanto, sairá primeiro no Min-Heap.

### Q2: Por que foi escolhido um Min-Heap e não um Max-Heap?
**R:** Por conveniência semântica com o Protocolo de Manchester. O nível mais grave é o 1 (Vermelho) e o menos grave é o 5 (Azul). Em um Min-Heap, o menor valor numérico fica na raiz, alinhando naturalmente o `score=1` com o topo de atendimento prioritário.
