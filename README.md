# Smart Triage - Sistema Hospitalar Inteligente

Aplicação web para triagem e gerenciamento de fluxo de atendimento em pronto-socorro baseada no **Protocolo de Manchester**, integrando conceitos de Estruturas de Dados, Banco de Dados Relacional, Orientação a Objetos e Inteligência Artificial.

---

## 🏥 Funcionalidades e Pilares

- **Estruturas de Dados (Fila de Prioridade):** Min-Heap binário manual para reordenação dinâmica de pacientes por gravidade clínica, preferência legal e ordem de chegada (FIFO).
- **Banco de Dados (SQLite):** Modelagem relacional normalizada com tabelas de pacientes, triagens e histórico de atendimentos.
- **CRUD e Transações:** Camada de repositório segura com integridade referencial, consultas parametrizadas e controle transacional.
- **Orientação a Objetos:** Modelagem de domínio com encapsulamento, herança (`PacientePreferencial`) e polimorfismo.
- **Classificação Inteligente:** Integração com Google Gemini API para análise de sintomas e sugestão de gravidade, acompanhada de fallback heurístico local offline.
- **Interface Web:** Painel operacional em FastAPI, Jinja2 e TailwindCSS com visão de recepção e consultório médico.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **Banco de Dados:** SQLite3
- **IA:** Google GenAI SDK (`gemini-2.5-flash`) com fallback offline
- **Frontend:** HTML5, TailwindCSS, JavaScript
- **Testes:** Pytest

---

## 📂 Estrutura do Projeto

```text
smart-triage/
├── app/
│   ├── core/               # Fila de prioridade (Min-Heap manual)
│   ├── database/           # Conexão SQLite e repositórios CRUD
│   ├── models/             # Classes de domínio e regras de negócio
│   ├── services/           # Serviço de classificação clínica (IA e fallback)
│   ├── static/             # Arquivos estáticos (CSS, JS)
│   ├── templates/          # Templates HTML da interface
│   └── main.py             # Rotas e inicialização da aplicação
├── tests/                  # Testes automatizados unitários e de integração
├── requirements.txt        # Dependências do projeto
└── README.md
```

---

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.10 ou superior
- Git

### 2. Instalação

```bash
# Clone o repositório
git clone https://github.com/luisveras-dev/smart-triage-manchester.git
cd smart-triage-manchester

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração (Opcional)
Para utilizar o modelo do Google Gemini na classificação, defina a variável de ambiente com sua chave de API:

```bash
export GEMINI_API_KEY="sua_chave_aqui"
```

> **Nota:** Caso a chave não seja configurada ou ocorra instabilidade de rede, o sistema ativa automaticamente o fallback heurístico offline baseado no Protocolo de Manchester.

### 4. Executando o Servidor

```bash
uvicorn app.main:app --reload
```

Acesse a interface no navegador: **`http://localhost:8000`**

---

## 🧪 Executando os Testes

Para rodar toda a suíte de testes automatizados:

```bash
pytest -v
```
