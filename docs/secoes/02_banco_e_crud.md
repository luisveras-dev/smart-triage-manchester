# Pilar 2 & 3: Banco de Dados & CRUD (Persistência e Repository)

**Responsável:** Integrante responsável por Banco de Dados / CRUD  
**Arquivos principais no código:** `app/database/schema.sql` e `app/database/connection.py`

---

## 1. Modelagem Relacional (SQLite)
A persistência utiliza o **SQLite3** nativo do Python, com integridade referencial habilitada via `PRAGMA foreign_keys = ON`. A modelagem é dividida em três tabelas relacionais com cardinalidade $1:N$:

```text
[ pacientes ]  1 ──< N  [ triagens ]  1 ──< N  [ atendimentos ]
```

### Estrutura das Tabelas:
1. **`pacientes`:**
   * `id`: Chave primária autoincremento (`INTEGER PRIMARY KEY AUTOINCREMENT`).
   * `cpf`: Chave natural única (`TEXT UNIQUE NOT NULL`).
   * `nome`, `idade`, `eh_preferencial`, `criado_em`.
2. **`triagens`:**
   * `id`: Chave primária.
   * `paciente_id`: Chave estrangeira (`FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE`).
   * `sintomas`, `gravidade_score`, `cor_manchester`, `tempo_maximo_minutos`, `justificativa_ia`, `status` (`AGUARDANDO`, `ATENDIDO`).
3. **`atendimentos`:**
   * `id`: Chave primária.
   * `triagem_id`: Chave estrangeira (`FOREIGN KEY (triagem_id) REFERENCES triagens(id) ON DELETE CASCADE`).
   * `medico_responsavel`, `data_hora_chamada`, `observacoes`.

---

## 2. Padrão Repository e Camada de Aplicação (CRUD)
A classe `DatabaseManager` centraliza todo o acesso ao banco, desacoplando a camada web e de negócios do SQL puro.

### Principais Operações Implementadas:
* **Create (Inserção):** `salvar_paciente`, `salvar_triagem`, `registrar_atendimento`.
* **Read (Consultas e Joins):**
  * `obter_paciente_por_id(id)`: Busca pontual por chave primária.
  * `listar_triagens_ativas()`: `INNER JOIN` entre `triagens` e `pacientes` filtrando `status = 'AGUARDANDO'`.
  * `listar_historico_atendimentos()`: Junção tripla (`atendimentos` + `triagens` + `pacientes`) ordenada por data decrescente.
* **Update (Atualização):** `atualizar_status_triagem`, atualização de cadastro de paciente já existente por CPF.
* **Delete (Exclusão Cascata):** Garantida pelo motor do SQLite através de `ON DELETE CASCADE`.

---

## 3. Segurança e Propriedades ACID

### A. Prevenção de SQL Injection
Todas as consultas utilizam **Prepared Statements** com placeholders parametrizados (`?`), nunca concatenação de strings:
```python
# Correto e seguro contra injeção de SQL:
cursor.execute("SELECT * FROM pacientes WHERE cpf = ?", (cpf,))
```

### B. Controle Transacional (Commit / Rollback)
O método `_obter_conexao()` implementa um Gerenciador de Contexto (`@contextmanager`) que garante a atomicidade das operações:
```python
@contextmanager
def _obter_conexao(self):
    conn = sqlite3.connect(self.db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()      # Grava as alterações se tudo correr bem
    except Exception:
        conn.rollback()    # Desfaz alterações em caso de erro (Atomicidade)
        raise
    finally:
        conn.close()       # Fecha a conexão garantindo liberação de recursos
```

---

## 4. Perguntas Frequentes para Apresentação

### Q1: Por que o SQLite precisa do `PRAGMA foreign_keys = ON`?
**R:** Por padrão histórico de retrocompatibilidade, o SQLite vem com o suporte a chaves estrangeiras desligado. O comando `PRAGMA foreign_keys = ON;` é executado a cada conexão para que o banco valide e impeça inserções de triagens para pacientes inexistentes e execute a exclusão em cascata.

### Q2: O que acontece se o mesmo paciente for admitido mais de uma vez?
**R:** A regra no `salvar_paciente` verifica se o CPF já existe. Se existir, apenas atualiza os dados cadastrais (ex: idade, preferência) e reaproveita o `paciente_id`, vinculando a nova triagem ao mesmo registro histórico de paciente sem duplicar o CPF.
