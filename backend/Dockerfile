FROM python:3.11-slim

# Binaires système nécessaires au traitement audio
RUN apt-get update && apt-get install -y \
    fluidsynth \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Utilisateur non-root : bonne pratique de sécurité,
# évite qu'un conteneur compromis ait les pleins droits sur le système hôte
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]