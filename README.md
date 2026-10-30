# Smart Triage - Sistema Hospitalar Inteligente

> Mini-sistema de triagem médica baseado no **Protocolo de Manchester**, integrando os cinco pilares fundamentais da Ciência da Computação: **Estruturas de Dados Básicas**, **Banco de Dados**, **Database Application (CRUD)**, **Programação Orientada a Objetos (POO)** e **Inteligência Artificial (IA)**.

---

## 🏛️ Os 5 Pilares no Projeto

| Pilar | Implementação no Projeto | Responsável |
| :--- | :--- | :--- |
| **1. Estruturas de Dados** | Fila de Prioridade implementada com **Min-Heap manual** $O(\log n)$ para ordenação dinâmica dos pacientes por gravidade. | Aluno 2 |
| **2. Banco de Dados** | Modelagem relacional em **SQLite** com tabelas `pacientes`, `triagens` e `atendimentos`. | Aluno 1 |
| **3. Database Application** | Camada de repositório com operações de **CRUD**, transações seguras e consultas de histórico. | Aluno 1 |
| **4. Orientação a Objetos** | Classes de domínio (`Paciente`, `PacientePreferencial`, `Triagem`), uso de herança, encapsulamento e polimorfismo. | Aluno 3 |
| **5. Inteligência Artificial** | **Google Gemini API** para interpretar os sintomas clínicos em texto livre e sugerir a classificação de risco (Manchester), com fallback offline. | Aluno 4 |

---

## 🚀 Arquitetura e Tecnologias

- **Linguagem:** Python 3.11+
- **API Web:** FastAPI + Uvicorn
- **Banco de Dados:** SQLite3 nativo
- **Inteligência Artificial:** Google GenAI SDK (Gemini 2.0 / 1.5)
- **Frontend:** HTML5 + TailwindCSS + JavaScript Vanilla (Dashboard hospitalar responsivo)

---

## 📂 Estrutura de Pastas

```text
smart-triage/
├── app/
│   ├── core/               # Estruturas de dados (Min-Heap manual)
│   ├── database/           # Conexão SQLite e repositórios CRUD
│   ├── models/             # Classes de domínio POO
│   ├── services/           # Serviço de IA (Gemini API)
│   ├── static/             # CSS e JavaScript do painel
│   ├── templates/          # HTML da interface hospitalar
│   └── main.py             # Aplicação FastAPI e rotas
├── scripts/                # Scripts de setup e automação
├── tests/                  # Testes unitários de cada pilar
├── DEFESA_TECNICA.md       # Guia completo para a sabatina do professor
└── README.md
```

---

## 📋 Como Executar o Projeto

```bash
# 1. Crie o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure a chave da API do Gemini (opcional - possui fallback offline)
export GEMINI_API_KEY="sua_chave_aqui"

# 4. Inicie o sistema
uvicorn app.main:app --reload
```
Acesse `http://localhost:8000` no seu navegador.
