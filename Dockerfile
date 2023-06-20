# Use a imagem base do Python
FROM python:3.9

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie os arquivos de requisitos do projeto para o contêiner
COPY requirements.txt .

# Instale as dependências do projeto
RUN pip install -r requirements.txt

# Copie o código do projeto para o contêiner
COPY . .

# Expõe a porta em que o servidor Django estará em execução
EXPOSE 8000

# Execute o comando para iniciar o servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]