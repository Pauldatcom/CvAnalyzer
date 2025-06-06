# Étape 1 : Image de base officielle
FROM python:3.10-slim

# Étape 2 : Dépendances système (pour Playwright)
RUN apt-get update && apt-get install -y wget curl unzip fonts-liberation libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 libxcomposite1 libxrandr2 libxdamage1 libgbm1 libasound2 libxshmfence1 libxss1 libxext6 libxfixes3 libx11-xcb1 libx11-dev libdrm2 ca-certificates

# Étape 3 : Créer un dossier d'app
WORKDIR /app

# Étape 4 : Copier tout le code
COPY . .

# Étape 5 : Installer les paquets Python
RUN pip install --no-cache-dir -r requirements.txt

# Étape 6 : Installer les navigateurs Playwright
RUN playwright install --with-deps

# Étape 7 : Lancer l’app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
