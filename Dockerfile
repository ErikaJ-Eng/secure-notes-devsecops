# Imagen base mínima y oficial (reduce superficie de ataque)
FROM python:3.12-slim

# Evita ejecutar como root (buena práctica de seguridad de contenedores)
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Instala dependencias primero (mejor cacheo de capas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY . .

USER appuser

EXPOSE 5000

# Arranque productivo con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
