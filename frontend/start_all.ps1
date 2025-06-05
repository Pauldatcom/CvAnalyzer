# 1. Activer environnement
Write-Host "🔄 Activation de l'environnement Python..."
.\env\Scripts\Activate.ps1

# 2. Démarrer LiveKit via Docker
Write-Host "🚀 Lancement de LiveKit..."
Start-Process powershell -ArgumentList "docker run --rm -p 7880:7880 -p 7881:7881 -e `"LIVEKIT_KEYS=mykey: mysecret`" -e LIVEKIT_REDIS_HOST=localhost livekit/livekit-server --dev"

# 3. Démarrer FastAPI
Write-Host "🌐 Lancement de l'API Mistral + Whisper..."
Start-Process powershell -ArgumentList "uvicorn server:app --reload --port 8000"

# 4. Lancer Streamlit
Write-Host "🖥️ Lancement de Streamlit..."
streamlit run app.py
