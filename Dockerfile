# Étape 1 : choisir l'image de base
FROM python:3.11-slim

# Étape 2 : définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3 : copier les fichiers de dépendances
COPY requirements.txt .

# Étape 4 : mettre à jour pip et installer les dépendances
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Étape 5 : copier le reste du projet
COPY . .

# Étape 6 : exposer le port de l'application Flask
EXPOSE 5000

# Étape 7 : commande pour lancer l'application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
