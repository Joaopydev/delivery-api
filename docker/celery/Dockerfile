# Dockerfile para o Celery worker
FROM python:3.11-slim


WORKDIR /app


# instalar dependências do sistema (se necessário)
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
&& rm -rf /var/lib/apt/lists/*


# copia apenas requirements primeiro para aproveitar cache do Docker
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


# copia todo o código (em dev é útil montar volume no docker-compose)
COPY . /app


# usuário não-root opcional (manter como root em dev facilita coisas)


# default command (sobrescrito pelo docker-compose command)
CMD ["bash"]