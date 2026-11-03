# Pilar 5: Inteligência Artificial & Testes E2E

**Responsável:** Integrante responsável por IA / Testes  
**Arquivos principais no código:** `app/services/ai_service.py`, `tests/` e interface web (`app/main.py`)

---

## 1. O Pilar de IA: Classificação Inteligente de Manchester
O serviço `AIService` é encarregado de ler a queixa do paciente em linguagem natural e determinar a cor e gravidade do Protocolo de Manchester.

### A. Integração com a Google Gemini API
* **Modelo utilizado:** `gemini-2.5-flash` via SDK oficial `google-genai`.
* **Prompt Engineering Estruturado:** O modelo recebe instruções clínicas detalhadas dos 5 níveis de Manchester e um contrato rígido de saída em JSON:
  ```json
  {
    "cor": "VERMELHO",
    "score": 1,
    "justificativa": "Dor torácica súbita com irradiação indica suspeita de infarto agudo.",
    "tempo_maximo_minutos": 0
  }
  ```
* **Sanitização de Saída:** Extração do bloco JSON por expressão regular (`re.search`), garantindo tolerância caso o modelo devolva blocos de código com markdown.

### B. Fallback Heurístico Clínico Offline (Tolerância a Falhas)
Em sistemas críticos de saúde, uma falha de conexão com a nuvem ou estouro de cota da API não pode parar o hospital.
* O sistema possui uma camada de **degradação graciosa (*graceful degradation*)**:
* Se a chave de API não for fornecida, houver timeout ou queda de internet, o método `_classificar_com_fallback` é acionado automaticamente.
* Utiliza um analisador léxico-clínico ponderado por palavras-chave de risco (ex: parada, infarto, tiro, fratura exposta, febre, dor de cabeça leve).

---

## 2. Validação e Testes Automatizados
O projeto conta com suíte de testes com `pytest` cobrindo cada pilar de forma isolada:

| Arquivo de Teste | O que é validado |
| :--- | :--- |
| `tests/test_priority_queue.py` | Min-Heap manual, inserção, remoção, desempate FIFO e preferencial. |
| `tests/test_database.py` | Conexão SQLite, CRUD, transações com rollback e integridade referencial. |
| `tests/test_models.py` | Validações `@property`, herança `PacientePreferencial` e polimorfismo. |
| `tests/test_api_ui.py` | Rotas FastAPI da triagem, listagem da fila e chamada de atendimento. |

Para rodar todos os testes automatizados:
```bash
pytest -v
```

---

## 3. Roteiro de Teste do Fluxo Completo (Ponta a Ponta)

Para demonstrar o sistema funcionando na apresentação ao vivo ou capturar prints/vídeo:

1. **Iniciar a aplicação:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Acesse no navegador: `http://localhost:8000`.

2. **Simulação do Fluxo Clínico:**
   * **Cenário 1 (Pouco urgente):** Cadastre *João Silva* (35 anos), queixa: *"Dor de cabeça leve desde ontem"*.
     * **Resultado:** IA classifica como **Verde** (Score 4) ou **Azul** (Score 5).
   * **Cenário 2 (Emergência imediata):** Cadastre *Maria Santos* (68 anos, preferencial), queixa: *"Dor no peito forte irradiando para o braço esquerdo e falta de ar súbita"*.
     * **Resultado:** IA classifica como **Vermelho** (Score 1).
   * **Verificação da Fila (Min-Heap):** Maria ultrapassa automaticamente João e assume a 1ª posição da fila.
   * **Atendimento Médico:** O médico clica em *"Chamar Próximo Paciente"* no painel. O sistema chama Maria primeiro e registra o atendimento no histórico do banco de dados.

---

## 4. Evidências do Sistema em Funcionamento
As capturas de tela e/ou links para gravação de tela demonstrando o fluxo devem ser salvos na pasta:
`docs/evidencias/`

* `docs/evidencias/01_triagem_ia.png` (Tela de cadastro e sugestão da cor pela IA)
* `docs/evidencias/02_fila_minheap.png` (Visualização da fila de prioridade reordenada)
* `docs/evidencias/03_atendimento_historico.png` (Painel médico e registro de atendimento)

---

## 5. Perguntas Frequentes para Apresentação

### Q1: O que acontece se a internet cair durante a apresentação do professor?
**R:** O sistema foi blindado para esse cenário. O método `classificar_sintomas` captura qualquer erro da chamada de rede e comuta instantaneamente para o fallback heurístico local. A triagem continua funcionando offline com classificação clínica correta e resposta instantânea.

### Q2: A IA toma a decisão final sobre o paciente?
**R:** Não. Na arquitetura hospitalar e na interface, a IA atua como **suporte à decisão clínica**. Ela sugere a classificação com justificativa fundamentada, mas o enfermeiro ou médico na triagem pode confirmar ou ajustar a gravidade antes de consolidar na fila.
