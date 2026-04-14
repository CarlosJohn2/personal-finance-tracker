# 💰 Personal Finance Tracker

<div align="center">

[![CI](https://github.com/seu-usuario/personal-finance-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/seu-usuario/personal-finance-tracker/actions)
[![Coverage](https://codecov.io/gh/seu-usuario/personal-finance-tracker/branch/main/graph/badge.svg)](https://codecov.io/gh/seu-usuario/personal-finance-tracker)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Sistema CLI de controle financeiro pessoal — Python + MySQL + Rich**

*Gerencie receitas, despesas, categorias e metas financeiras direto do terminal.*

</div>

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 📝 **CRUD de Transações** | Adicione, liste e remova receitas e despesas |
| 🏷️ **Categorias** | Categorias customizáveis com ícones e cores |
| 📊 **Relatórios** | Resumo mensal e histórico anual com gráficos |
| 💾 **Exportação** | Exporte para CSV (Excel) ou PDF |
| 🖥️ **Dashboard** | Painel bonito com saldo, alertas e top gastos |
| 🎯 **Metas** | Crie metas financeiras com acompanhamento de progresso |
| 🏦 **Multi-conta** | Gerencie corrente, poupança, investimentos e carteira |
| 🔔 **Alertas** | Notificações automáticas de metas próximas do prazo |

---

## 🖥️ Preview

```
  💰 Personal Finance Tracker
     Hoje: domingo, 13 de abril de 2025

╭─────────────────────────────╮  ╭─────────────────────────────────╮
│          Saldo Total        │  │       📅 Abril/2025             │
│                             │  │                                  │
│   📈  +R$ 14.320,00        │  │   Receitas    R$   6.000,00     │
╰─────────────────────────────╯  │   Despesas    R$   2.840,00     │
                                  │   ────────────────────────────   │
                                  │   Saldo      +R$   3.160,00     │
                                  │                                  │
                                  │   15 transações em Abril/2025   │
                                  ╰─────────────────────────────────╯

╭────────────────────────────────────────────────────────────────────╮
│  🕐 Transações Recentes                                            │
│  13/04  💼 Salário mensal — empresa XYZ     +R$  6.000,00         │
│  12/04  🍔 Supermercado Pão de Açúcar        -R$    342,50         │
│  10/04  🏠 Aluguel                           -R$  1.800,00         │
│  08/04  🎮 PlayStation Store                  -R$    299,90         │
│  05/04  💻 Projeto React — cliente A         +R$  2.500,00         │
╰────────────────────────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────╮
│  🔔 Alertas de Metas                                 │
│  📅  Meta 'Notebook Novo' vence em 231 dias (33.3%)  │
╰──────────────────────────────────────────────────────╯
```

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/personal-finance-tracker.git
cd personal-finance-tracker
```

### 2. Crie o ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements-dev.txt
pip install -e .
```

### 4. Suba o MySQL com Docker

```bash
docker-compose up -d db
```

Aguarde o healthcheck ficar verde (cerca de 30 segundos):

```bash
docker-compose ps   # STATUS: healthy
```

### 5. Configure o ambiente

```bash
cp .env.example .env
# Edite .env se necessário (padrões funcionam com o Docker)
```

### 6. Execute as migrations

```bash
alembic upgrade head
```

### 7. (Opcional) Popule com dados de exemplo

```bash
python scripts/seed.py
```

### 8. Use!

```bash
financa            # Abre o dashboard
financa --help     # Todos os comandos
```

---

## 🐳 Uso com Docker Completo

```bash
# Subir banco + rodar migrations
docker-compose up -d db
docker-compose --profile migrate run --rm migrate

# Popular com dados de exemplo
docker-compose --profile seed run --rm seed

# Abrir CLI interativo
docker-compose run --rm app
```

---

## 📋 Comandos

### Dashboard
```bash
financa                    # Exibe o painel principal
```

### Transações
```bash
financa transacao adicionar                        # Adicionar (interativo)
financa transacao listar                           # Listar recentes
financa transacao listar --mes 4 --ano 2025       # Filtrar por mês
financa transacao deletar 42                       # Remover por ID
```

### Categorias
```bash
financa categoria listar                  # Listar todas
financa categoria listar --tipo despesa   # Filtrar por tipo
financa categoria adicionar               # Adicionar (interativo)
financa categoria deletar 5               # Remover por ID
```

### Relatórios
```bash
financa relatorio mensal                         # Mês atual
financa relatorio mensal --mes 3 --grafico       # Com gráfico de pizza
financa relatorio anual                          # Ano atual
financa relatorio anual --ano 2024 --grafico     # Com gráfico de barras
financa relatorio exportar --formato csv         # Exportar CSV
financa relatorio exportar --formato pdf         # Exportar PDF
```

### Metas
```bash
financa meta listar              # Metas ativas
financa meta listar --todas      # Incluir encerradas
financa meta adicionar           # Criar meta (interativo)
financa meta depositar 1         # Registrar aporte
financa meta encerrar 2          # Encerrar meta
```

---

## 🧪 Testes

```bash
# Rodar todos os testes
pytest

# Com saída detalhada
pytest -v

# Sem verificação de cobertura (mais rápido)
pytest --no-cov

# Teste específico
pytest tests/test_transacao_service.py -v

# Ver relatório de cobertura HTML
open htmlcov/index.html
```

---

## 🏗️ Arquitetura

```
src/
├── cli/                    # Camada de apresentação (Typer + Rich)
│   ├── commands/           # Subcomandos da CLI
│   └── ui/                 # Tabelas, painéis e prompts Rich
├── services/               # Regras de negócio
├── repositories/           # Acesso a dados (queries SQLAlchemy)
├── models/                 # Modelos ORM (SQLAlchemy 2.0)
├── database/               # Conexão e session management
└── config.py               # Configurações via .env
```

**Padrão arquitetural:** MVC adaptado para CLI

```
CLI (View) → Service (Controller) → Repository → Model (SQLAlchemy)
```

---

## 🗄️ Banco de Dados

```sql
categorias (id, nome, icone, tipo, cor)
    │
    ├── transacoes (id, descricao, valor, tipo, data, conta_id, categoria_id)
    │       │
    │       └── contas (id, nome, tipo, saldo_inicial)
    │
    └── metas (id, nome, valor_alvo, valor_atual, data_limite, ativa)
```

Índices criados para performance em consultas por data, conta e categoria.

---

## 📦 Dependências Principais

| Biblioteca | Versão | Uso |
|---|---|---|
| `typer` | 0.12.3 | Framework CLI |
| `rich` | 13.7.1 | UI no terminal |
| `sqlalchemy` | 2.0.30 | ORM |
| `alembic` | 1.13.1 | Migrations |
| `mysql-connector-python` | 8.3.0 | Driver MySQL |
| `matplotlib` | 3.8.4 | Gráficos |
| `reportlab` | 4.2.0 | Exportação PDF |
| `questionary` | 2.0.1 | Prompts interativos |

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/minha-funcionalidade`
3. Instale os hooks: `pre-commit install`
4. Faça suas mudanças com testes
5. Verifique: `pytest && flake8 src/ tests/ && black --check src/ tests/`
6. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** — veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">

Feito com ❤️ e Python

</div>
