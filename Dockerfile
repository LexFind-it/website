FROM openjdk:11-slim

# Installa Python
RUN apt-get update && apt-get install -y python3 python3-pip && apt-get clean

# Copia i file richiesti
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt

# Copia il codice
COPY . /app

# Espone la porta di Streamlit
EXPOSE 8501

# Comando di avvio
CMD ["streamlit", "run", "test_webapp.py", "--server.port=8080", "--server.address=0.0.0.0"]
