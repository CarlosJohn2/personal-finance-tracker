# 📖 Referência de Comandos

## Visão Geral

```
financa [COMANDO] [SUBCOMANDO] [OPÇÕES]
```

Sem argumentos, exibe o **dashboard** principal.

---

## Dashboard

```bash
financa
financa dashboard
```

Exibe o painel completo com saldo, resumo do mês, transações recentes, top gastos e alertas de metas.

---

## Transações

### Adicionar (interativo)
```bash
financa transacao adicionar
```

Guia interativo com prompts para tipo, descrição, valor, data, conta e categoria.

### Listar
```bash
financa transacao listar                    # Últimas 50 transações
financa transacao listar --mes 4 --ano 2025 # Filtrar por mês
financa transacao listar --limite 100       # Aumentar limite
```

| Opção | Alias | Descrição |
|-------|-------|-----------|
| `--mes` | `-m` | Mês (1–12) |
| `--ano` | `-a` | Ano (ex: 2025) |
| `--limite` | `-l` | Máximo de registros (padrão: 50) |

### Deletar
```bash
financa transacao deletar 42   # Remove transação com ID 42
```

---

## Categorias

### Listar
```bash
financa categoria listar               # Todas as categorias
financa categoria listar --tipo despesa  # Somente despesas
financa categoria listar --tipo receita  # Somente receitas
```

### Adicionar (interativo)
```bash
financa categoria adicionar
```

### Deletar
```bash
financa categoria deletar 5   # Remove categoria com ID 5
```

> Categorias vinculadas a transações não podem ser removidas.

---

## Relatórios

### Mensal
```bash
financa relatorio mensal                         # Mês atual
financa relatorio mensal --mes 3 --ano 2025      # Março/2025
financa relatorio mensal --mes 4 --grafico       # Com gráfico de pizza
```

Gráficos são salvos em `charts/pizza_AAAA_MM.png`.

### Anual
```bash
financa relatorio anual                 # Ano atual
financa relatorio anual --ano 2024      # Ano específico
financa relatorio anual --grafico       # Com gráfico de barras
```

Gráficos são salvos em `charts/anual_AAAA.png`.

### Exportar
```bash
financa relatorio exportar                              # CSV do mês atual
financa relatorio exportar --mes 4 --ano 2025           # CSV específico
financa relatorio exportar --formato pdf                # PDF do mês atual
financa relatorio exportar --mes 3 --formato pdf        # PDF específico
```

Arquivos são salvos em `exports/`.

---

## Metas

### Listar
```bash
financa meta listar           # Somente metas ativas
financa meta listar --todas   # Inclui metas encerradas
```

### Adicionar (interativo)
```bash
financa meta adicionar
```

### Depositar aporte
```bash
financa meta depositar 1   # Registra aporte na meta ID 1
```

### Encerrar
```bash
financa meta encerrar 2   # Marca meta ID 2 como inativa
```

---

## Exemplos de Uso Rápido

```bash
# Ver dashboard
financa

# Registrar uma receita
financa transacao adicionar

# Ver gastos de março com gráfico
financa relatorio mensal --mes 3 --grafico

# Exportar PDF de fevereiro
financa relatorio exportar --mes 2 --formato pdf

# Ver progresso de todas as metas
financa meta listar

# Ver histórico anual completo com gráfico
financa relatorio anual --grafico
```
