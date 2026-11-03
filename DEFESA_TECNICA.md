# Documentação de Arquitetura e Decisões Técnicas

> **Projeto:** Smart Triage - Sistema Hospitalar Inteligente com Protocolo de Manchester  
> **Disciplina:** Estrutura de Dados e Pilares da Computação  
> **Integrantes:** Todos os membros do grupo  

---

## 🏥 Visão Geral do Sistema
O **Smart Triage** é uma aplicação hospitalar desenvolvida para gerenciar o fluxo de atendimento em pronto-socorro utilizando o **Protocolo de Manchester**. O objetivo é priorizar o atendimento de acordo com a gravidade clínica e assegurar os critérios legais de preferência e ordem de chegada (FIFO).

O projeto foi construído integrando de forma coesa cinco áreas essenciais da Computação:
1. **Estruturas de Dados:** Fila de Prioridade implementada com Min-Heap Binário manual $\mathcal{O}(\log n)$.
2. **Banco de Dados:** Modelagem relacional normalizada em SQLite com integridade referencial.
3. **Database Application (CRUD):** Camada de repositório segura contra SQL Injection e controle de transações.
4. **Programação Orientada a Objetos (POO):** Encapsulamento estrito, herança e polimorfismo de regras de desempate.
5. **Inteligência Artificial (IA):** Análise clínica de queixas via Google Gemini com tolerância a falhas (fallback heurístico offline).

---

## 🏛️ Estrutura Detalhada por Pilar

A documentação aprofundada de cada pilar, contendo as análises assintóticas, decisões de design e perguntas frequentes para a apresentação, está organizada nos módulos abaixo:

| Pilar | Descrição Técnica | Documento Completo |
| :--- | :--- | :---: |
| **1. Estruturas de Dados** | Min-Heap manual, complexidade das operações, tupla comparativa de desempate e relações de índice. | [01_estruturas_de_dados.md](docs/secoes/01_estruturas_de_dados.md) |
| **2 & 3. Banco de Dados & CRUD** | Esquema das tabelas (`pacientes`, `triagens`, `atendimentos`), Repository pattern, prevenção de SQL injection e transações ACID. | [02_banco_e_crud.md](docs/secoes/02_banco_e_crud.md) |
| **4. Orientação a Objetos** | Classes de domínio, encapsulamento com `@property`, herança (`PacientePreferencial`) e método polimórfico de score. | [03_poo.md](docs/secoes/03_poo.md) |
| **5. Inteligência Artificial & Testes** | Integração com Gemini API, prompt engineering, fallback heurístico offline, suíte de testes e fluxo E2E. | [04_ia_e_testes.md](docs/secoes/04_ia_e_testes.md) |

---

## 🔄 Fluxo de Dados Ponta a Ponta (End-to-End)

```text
[ Paciente Chega ] 
       │
       ▼
[ Entrada de Dados ] ──> Dados cadastrais e queixa clínica em texto livre
       │
       ▼
[ Análise de IA ] ────> Google Gemini API interpreta sintomas (ou fallback offline)
                         Retorna: Cor de Manchester, Score (1-5) e Justificativa
       │
       ▼
[ Persistência BD ] ───> Salva/atualiza Paciente e registra Triagem no SQLite
       │
       ▼
[ Min-Heap Fila ] ────> Insere ItemFila com tupla (score, preferencial, timestamp)
                         Reorganiza a prioridade em O(log n)
       │
       ▼
[ Chamada Médica ] ───> Médico chama o próximo da fila (Raiz do Heap O(1) / O(log n))
                         Atualiza status no SQLite e registra o Atendimento
```

---

## 🚀 Como Executar o Projeto e os Testes

```bash
# 1. Ativar o ambiente virtual
source venv/bin/activate

# 2. Executar a suíte de testes automatizados
pytest -v

# 3. Iniciar o servidor web
uvicorn app.main:app --reload
```
Acesse o sistema no navegador: `http://localhost:8000`.
