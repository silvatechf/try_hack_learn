FROM python:3.11-slim

# Instala dependências para download do binário estático do Docker CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Baixa e instala o binário oficial estático do Docker CLI diretamente para /usr/bin/docker
RUN ARCH="" && case $(uname -m) in \
        x86_64) ARCH="x86_64" ;; \
        aarch64) ARCH="aarch64" ;; \
        *) echo "Unsupported architecture" && exit 1 ;; \
    esac \
    && curl -fsSL "https://download.docker.com/linux/static/stable/${ARCH}/docker-26.1.0.tgz" -o docker.tgz \
    && tar xzvf docker.tgz --strip 1 -C /usr/local/bin docker/docker \
    && rm docker.tgz

# Garante permissão de execução e visibilidade no PATH
RUN chmod +x /usr/local/bin/docker

ENV PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8003
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]