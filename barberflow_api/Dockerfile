# Usa a imagem oficial do Python (baseada em Debian Buster)
FROM python:3.9-slim-buster

# Instala as ferramentas de compilação essenciais
# Esta é a linha que corrige o erro de instalação do pip
RUN apt-get update && apt-get install -y build-essential

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .
# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da aplicação para o diretório de trabalho
COPY . .

# Expõe a porta que a aplicação Flask vai usar
EXPOSE 5000

# Comando para iniciar a aplicação quando o contêiner rodar
CMD ["python", "src/main.py"]
