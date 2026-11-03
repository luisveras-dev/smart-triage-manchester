# Pilar 4: Programação Orientada a Objetos (POO)

**Responsável:** Integrante responsável por POO  
**Arquivos principais no código:** `app/models/paciente.py` e `app/models/triagem.py`

---

## 1. Os 4 Pilares da POO no Projeto

### A. Encapsulamento
* Todos os atributos de estado nas classes `Paciente`, `PacientePreferencial` e `Triagem` são protegidos por convenção com prefixo underscore (ex: `self._nome`, `self._cpf`, `self._grau_risco`).
* O acesso e a modificação são controlados por **decoradores `@property` e `@setter`**, impedindo estados inválidos:
  * O `setter` de `nome` valida se o valor não é vazio ou apenas espaços.
  * O `setter` de `idade` impede valores negativos ou maiores que 130 anos.
  * O CPF é sanitizado no construtor para conter apenas caracteres alfanuméricos.

### B. Herança
* A classe base `Paciente` modela um paciente geral do hospital.
* A classe `PacientePreferencial` herda de `Paciente` (`class PacientePreferencial(Paciente):`), reutilizando atributos como nome, CPF e idade via `super().__init__(...)` e especializando o comportamento com o atributo `motivo_preferencia` (ex: idoso, gestante, lactante, PcD conforme Lei nº 10.048/2000).

```text
       [ Paciente ]  (Geral, peso_desempate = 1)
            ▲
            │ extends
 [ PacientePreferencial ]  (Preferencial, peso_desempate = 0)
```

### C. Polimorfismo
* O método `peso_prioridade_desempate()` é sobrescrito na subclasse:
  * `Paciente.peso_prioridade_desempate()` retorna `1`.
  * `PacientePreferencial.peso_prioridade_desempate()` retorna `0`.
* O método `calcular_score_final(triagem)` calcula a chave da fila de forma polimórfica: a fila de prioridade não precisa saber se o paciente é comum ou preferencial através de `if/else`, ela apenas invoca `paciente.calcular_score_final(triagem)` e o objeto responde conforme sua classe em tempo de execução.

### D. Abstração e Tipagem Estrita
* O `GrauRisco` é implementado como uma `Enum` rica, encapsulando não apenas a cor, mas também o score numérico de 1 a 5, o tempo máximo de espera preconizado pelo Protocolo de Manchester e a descrição clínica.

---

## 2. Métodos de Serialização
Tanto `Paciente` quanto `Triagem` implementam o método `to_dict()`, permitindo exportar com facilidade os objetos de domínio para JSON nas rotas da API FastAPI e nos testes automatizados, sem acoplar a lógica de negócio à camada de apresentação.

---

## 3. Perguntas Frequentes para Apresentação

### Q1: Onde o polimorfismo é aplicado na prática na fila de atendimento?
**R:** Quando um item entra no Min-Heap (`ItemFila`), ele obtém sua prioridade chamando `self.paciente.calcular_score_final(self.triagem)`. Se o objeto for uma instância de `PacientePreferencial`, o método devolve peso `0`; se for um `Paciente` comum, devolve peso `1`. O Min-Heap trata ambos de forma idêntica e genérica através do contrato do método, sem verificar tipos com `isinstance`.

### Q2: Por que usar `@property` em vez de deixar os atributos públicos?
**R:** Para garantir o encapsulamento e a integridade dos dados clínicos. Se os atributos fossem públicos, qualquer parte do código poderia alterar a idade para um valor negativo ou o nome para vazio sem que o modelo pudesse validar ou emitir uma exceção.
