FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias primero (optimiza cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Puerto de Streamlit
EXPOSE 8501

# Comando para correr el dashboard
CMD ["streamlit", "run", "dashboards/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
