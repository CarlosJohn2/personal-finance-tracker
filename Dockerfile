FROM python:3.11-slim

# Metadados
LABEL maintainer="Personal Finance Tracker"
LABEL description="Sistema CLI de controle financeiro pessoal"

# Variáveis de build
ARG DEBIAN_FRONTEND=noninteractive

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Instala dependências Python (cache layer otimizado)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia código-fonte
COPY . .

# Instala o projeto em modo editável
RUN pip install --no-cache-dir -e .

# Cria diretórios de saída
RUN mkdir -p /app/exports /app/charts

# Usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash financa && \
    chown -R financa:financa /app
USER financa

# Entry point
ENTRYPOINT ["financa"]
CMD ["dashboard"]
