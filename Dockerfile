FROM python:3.11-slim

# Diretório de trabalho no container
WORKDIR /app

# Instalação de dependências do sistema necessárias para o psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalação das dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cópia do código-fonte
COPY . .

# Exposição da porta estipulada no desafio
EXPOSE 7777

# Execução do Streamlit na porta 7777
CMD ["streamlit", "run", "app.py", "--server.port=7777", "--server.address=0.0.0.0"]