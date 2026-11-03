# Guia de Contribuição da Equipe (Issue #06)

Este guia orienta como os 4 integrantes devem trabalhar de forma independente, abrindo seus respectivos Pull Requests sem conflitos de merge.

---

## 🎯 Divisão de Frentes de Trabalho

| Integrante | Arquivo Responsável | Sub-branch |
| :--- | :--- | :--- |
| **Pessoa 1** | `docs/secoes/01_estruturas_de_dados.md` | `docs/secao-ed` |
| **Pessoa 2** | `docs/secoes/02_banco_e_crud.md` | `docs/secao-bd-crud` |
| **Pessoa 3** | `docs/secoes/03_poo.md` | `docs/secao-poo` |
| **Pessoa 4** | `docs/secoes/04_ia_e_testes.md` | `docs/secao-ia-testes` |

---

## 💻 Passo a Passo para Cada Integrante

### 1. Atualizar e criar a sua sub-branch
No seu terminal, puxe as alterações mais recentes e crie sua branch a partir de `docs/arquitetura-e-testes`:

```bash
# Baixa as novidades do repositório
git fetch origin

# Cria sua branch baseada na branch de integração
git checkout -b docs/secao-ed origin/docs/arquitetura-e-testes
# (Substitua "docs/secao-ed" pelo nome da sua respectiva branch)
```

### 2. Editar o seu arquivo
* Abra o seu arquivo correspondente dentro da pasta `docs/secoes/`.
* Revise o conteúdo técnico, complemente exemplos se desejar e assegure-se de que domina todas as perguntas e respostas da sua seção.

### 3. Fazer o commit e push
```bash
git add docs/secoes/SEU_ARQUIVO.md
git commit -m "docs: revisa e consolida seção de [NOME DO SEU PILAR]"
git push origin docs/SUA_BRANCH
```

### 4. Abrir o Pull Request no GitHub
* Acesse o GitHub do repositório.
* Abra um Pull Request da sua branch apontando como **base** para: `docs/arquitetura-e-testes` *(NÃO selecione a main diretamente)*.
* Peça para um dos colegas revisar e aprovar o merge!

---

## 🏁 Finalização (Após a aprovação dos 4 PRs)
Quando os 4 PRs tiverem sido mesclados na branch `docs/arquitetura-e-testes`, o líder do grupo abrirá o Pull Request final da branch `docs/arquitetura-e-testes` para a `main`, encerrando oficialmente a Issue #06!
