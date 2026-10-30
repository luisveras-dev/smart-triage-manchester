#!/bin/bash
set -e

REPO_NAME="smart-triage-manchester"
REPO_DESC="Sistema Hospitalar de Triagem Medica Inteligente integrando os 5 Pilares da Computacao (ED, BD, CRUD, POO, IA)"

echo "=========================================================="
echo "🚀 Configurando o Repositório e Issues no GitHub via gh"
echo "=========================================================="

# 1. Verifica autenticação
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ Erro: Você ainda não está logado no GitHub CLI."
    echo "Execute 'gh auth login' no seu terminal e rode este script novamente."
    exit 1
fi

USER_NAME=$(gh api user -q .login)
echo "✅ Logado no GitHub como: $USER_NAME"

# 2. Cria o repositório remoto no GitHub (se ainda não existir)
if gh repo view "$USER_NAME/$REPO_NAME" >/dev/null 2>&1; then
    echo "ℹ️ Repositório $USER_NAME/$REPO_NAME já existe no GitHub."
else
    echo "📦 Criando repositório público: $REPO_NAME..."
    gh repo create "$REPO_NAME" --public --description "$REPO_DESC" --source=. --remote=origin
fi

# Garante o remote origin
git branch -M main
if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "https://github.com/$USER_NAME/$REPO_NAME.git"
fi

# 3. Faz o commit inicial e push
echo "📤 Fazendo push da branch main..."
git add .
git commit -m "chore: setup inicial do projeto e documentacao" || true
git push -u origin main

# 4. Criando Labels de Pilares
echo "🏷️ Criando labels personalizadas..."
gh label create "pilar:ed" --color "0E8A16" --description "Pilar 1 - Estruturas de Dados" --force || true
gh label create "pilar:bd" --color "1D76DB" --description "Pilar 2 - Modelagem de Banco" --force || true
gh label create "pilar:crud" --color "5319E7" --description "Pilar 3 - Database Application" --force || true
gh label create "pilar:poo" --color "FBCA04" --description "Pilar 4 - Orientação a Objetos" --force || true
gh label create "pilar:ia" --color "D93F0B" --description "Pilar 5 - Inteligência Artificial" --force || true
gh label create "pilar:ui" --color "006B75" --description "Interface Visual e Integração" --force || true

# 5. Criando as Issues
echo "📌 Cadastrando as 6 Issues do projeto..."

# Issue 1 - Banco e CRUD
gh issue create --title "Issue #01: [BD/CRUD] Modelagem do Banco SQLite e Repositório CRUD" \
--label "pilar:bd,pilar:crud" \
--body "### Responsável: Aluno 1 (Líder / Banco de Dados)
**Branch recomendada:** \`feat/database-sqlite\`

#### Contexto e Objetivo
Implementar a modelagem relacional em SQLite e a camada de repositório com operações de CRUD para persistência dos pacientes, triagens e atendimentos médicos.

#### Tarefas a Realizar
- [ ] Criar o schema DDL (\`app/database/schema.sql\`) com as tabelas:
  - \`pacientes\` (id, nome, cpf, data_nascimento, eh_preferencial, criado_em)
  - \`triagens\` (id, paciente_id, sintomas, gravidade_score, cor_manchester, justificativa_ia, status, criado_em)
  - \`atendimentos\` (id, triagem_id, medico_responsavel, data_hora_chamada, observacoes)
- [ ] Implementar a classe \`DatabaseManager\` em \`app/database/connection.py\` (conexão SQLite segura com suporte a transações).
- [ ] Implementar as operações de CRUD:
  - Inserir novo paciente e triagem
  - Listar pacientes com triagem ativa
  - Atualizar status para 'ATENDIDO' quando chamado pelo médico
- [ ] Criar testes unitários em \`tests/test_database.py\`.

#### Definição de Pronto (DoD)
- O banco de dados cria as tabelas automaticamente na inicialização se o arquivo \`.db\` não existir.
- O aluno responsável sabe explicar como transações ACID e commits funcionam no SQLite."

# Issue 2 - Fila de Prioridade (Min-Heap)
gh issue create --title "Issue #02: [ED] Fila de Prioridade com Min-Heap Manual O(log n)" \
--label "pilar:ed" \
--body "### Responsável: Aluno 2 (Estrutura de Dados)
**Branch recomendada:** \`feat/priority-queue-heap\`

#### Contexto e Objetivo
Implementar a estrutura de dados central do sistema: uma **Fila de Prioridade** usando **Min-Heap manual** em Python puro (sem usar apenas a biblioteca \`heapq\` opaca), garantindo ordenação dinâmica dos pacientes segundo a gravidade do Protocolo de Manchester.

#### Tarefas a Realizar
- [ ] Criar o módulo \`app/core/priority_queue.py\` contendo a classe \`PriorityQueue\`.
- [ ] Implementar os métodos essenciais:
  - \`inserir(item)\`: adiciona elemento e executa subida (\`_sift_up\`) - \$O(\log n)\$
  - \`remover_mais_urgente()\`: remove a raiz, move o último elemento e executa descida (\`_sift_down\`) - \$O(\log n)\$
  - \`obter_primeiro()\`: consulta a raiz sem remover - \$O(1)\$
  - \`listar_elementos()\`: retorna uma cópia ordenada para visualização
  - \`esta_vazia()\` e \`tamanho()\`
- [ ] Criar critérios de desempate:
  - 1º: Gravidade Manchester (1: Vermelho > 2: Laranja > 3: Amarelo > 4: Verde > 5: Azul)
  - 2º: Paciente Preferencial (idosos/gestantes ganham prioridade no desempate de mesma cor)
  - 3º: Horário de chegada (FIFO no mesmo nível de urgência)
- [ ] Criar testes unitários em \`tests/test_priority_queue.py\`.

#### Definição de Pronto (DoD)
- Testes cobrem inserção fora de ordem e remoção na ordem correta de prioridade.
- O aluno responsável sabe desenhar o Heap em formato de árvore e explicar a complexidade temporal \$O(\log n)\$ na sabatina."

# Issue 3 - POO e Modelos de Domínio
gh issue create --title "Issue #03: [POO] Modelos de Domínio com Herança, Encapsulamento e Polimorfismo" \
--label "pilar:poo" \
--body "### Responsável: Aluno 3 (Arquiteto POO)
**Branch recomendada:** \`feat/domain-oop-models\`

#### Contexto e Objetivo
Estruturar o domínio do sistema aplicando rigorosamente os pilares da Orientação a Objetos: Encapsulamento, Herança e Polimorfismo.

#### Tarefas a Realizar
- [ ] Criar \`app/models/paciente.py\`:
  - Classe base \`Paciente\` com atributos privados/protegidos (\`_nome\`, \`_cpf\`, \`_idade\`) com getters e setters (@property).
  - Subclasse \`PacientePreferencial\` herdando de \`Paciente\` (sobrescrevendo método polimórfico de prioridade).
- [ ] Criar \`app/models/triagem.py\`:
  - Enum \`GrauRisco\` (VERMELHO=1, LARANJA=2, AMARELO=3, VERDE=4, AZUL=5).
  - Classe \`Triagem\` que encapsula os sintomas, diagnóstico preliminar da IA e data/hora.
- [ ] Criar método polimórfico \`calcular_score_final()\` demonstrando polimorfismo em tempo de execução.
- [ ] Criar testes unitários em \`tests/test_models.py\`.

#### Definição de Pronto (DoD)
- Código limpo, tipado e com docstrings explicativas.
- O aluno responsável sabe apontar exatamente no código onde está o encapsulamento, a herança e o polimorfismo."

# Issue 4 - Inteligência Artificial com Gemini
gh issue create --title "Issue #04: [IA] Integração com Google Gemini API e Classificador Manchester" \
--label "pilar:ia" \
--body "### Responsável: Aluno 4 (Engenheiro de IA)
**Branch recomendada:** \`feat/gemini-ai-triage\`

#### Contexto e Objetivo
Integrar o sistema com a API do Google Gemini para realizar a leitura em linguagem natural dos sintomas clínicos do paciente e classificá-los com base nas diretrizes do Protocolo de Manchester.

#### Tarefas a Realizar
- [ ] Criar o módulo \`app/services/ai_service.py\` usando o SDK oficial \`google-genai\`.
- [ ] Construir o **System Prompt Clínico** que força a resposta em formato JSON estrito:
  \`\`\`json
  {
    \"cor\": \"VERMELHO\",
    \"score\": 1,
    \"justificativa\": \"Suspeita de infarto agudo do miocárdio\",
    \"tempo_maximo_minutos\": 0
  }
  \`\`\`
- [ ] Implementar **Fallback Heurístico de Emergência**: se a API falhar, não houver internet ou faltar chave no momento da apresentação, o sistema usa um analisador léxico local baseado em palavras-chave clínicas (ex: 'dor no peito' -> Vermelho).
- [ ] Criar testes em \`tests/test_ai_service.py\`.

#### Definição de Pronto (DoD)
- O sistema nunca quebra se a API falhar ou estiver sem internet.
- O aluno responsável sabe explicar o prompt engineering e o parser de resposta JSON."

# Issue 5 - Interface Visual e FastAPI
gh issue create --title "Issue #05: [UI/API] Interface Web Hospitalar e Conexão dos 5 Pilares" \
--label "pilar:ui" \
--body "### Responsável: Aluno 5 (Full-Stack / Interface)
**Branch recomendada:** \`feat/frontend-hospital-dashboard\`

#### Contexto e Objetivo
Criar uma interface web moderna, visualmente atraente e intuitiva para o hospital, orquestrada por uma API FastAPI que conecta os outros 4 pilares.

#### Tarefas a Realizar
- [ ] Configurar a aplicação FastAPI em \`app/main.py\` com rotas REST:
  - \`POST /api/triagem\`: recebe dados do paciente, chama IA, salva no banco e insere no Heap.
  - \`GET /api/fila\`: retorna a fila ordenada pelo Heap em tempo real.
  - \`POST /api/chamar-proximo\`: remove o paciente do topo do Heap e registra o atendimento.
- [ ] Construir a interface visual em \`app/templates/index.html\` com Tailwind CSS:
  - **Aba 1 (Recepção):** Formulário de triagem com botão animado de análise por IA.
  - **Aba 2 (Painel ao Vivo):** Quadro de espera com badges coloridos piscantes (Vermelho, Laranja, Amarelo, etc.).
  - **Aba 3 (Consultório Médico):** Visualização do próximo paciente a ser atendido e histórico.

#### Definição de Pronto (DoD)
- A tela atualiza a fila de pacientes sem necessidade de recarregar a página inteira.
- O aluno responsável sabe explicar como a interface conversa com os endpoints da API."

# Issue 6 - Documentação e Sabatina
gh issue create --title "Issue #06: [DOCS] Testes End-to-End e Guia de Blindagem da Sabatina" \
--label "pilar:ed,pilar:bd,pilar:crud,pilar:poo,pilar:ia" \
--body "### Responsável: Todos os 5 Alunos
**Branch recomendada:** \`docs/sabatina-defense-guide\`

#### Contexto e Objetivo
Consolidar a documentação final e o roteiro de estudo com perguntas e respostas para a sabatina do professor, garantindo que nenhum membro perca pontos.

#### Tarefas a Realizar
- [ ] Criar o arquivo \`DEFESA_TECNICA.md\` com as perguntas frequentes de cada pilar.
- [ ] Realizar uma simulação de perguntas (Mock Interview) entre os 5 alunos do grupo.
- [ ] Gravar um vídeo ou gerar prints do sistema funcionando para anexar na entrega.

#### Definição de Pronto (DoD)
- Todos os 5 membros dominam a explicação de todos os módulos do código."

echo "=========================================================="
echo "🎉 Repositório, Labels e 6 Issues criadas com sucesso!"
echo "Acesse: https://github.com/$USER_NAME/$REPO_NAME"
echo "=========================================================="
