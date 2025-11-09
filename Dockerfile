FROM python:3.10-slim

# Créer un dossier pour l'app
WORKDIR /app

# Copier les fichiers
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Le port utilisé par Render
EXPOSE 10000

# Lancer l'app avec Gunicorn (remplace app:app si besoin)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
