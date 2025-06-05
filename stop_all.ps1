Write-Host "🛑 Arrêt des processus Streamlit, FastAPI et Docker..."

# Arrêter les processus Streamlit
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*streamlit*" } | ForEach-Object { Stop-Process $_.Id -Force }

# Arrêter les processus Uvicorn (FastAPI)
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*uvicorn*" } | ForEach-Object { Stop-Process $_.Id -Force }

# Arrêter tous les conteneurs Docker (optionnel mais radical)
docker ps -q | ForEach-Object { docker stop $_ }

# 🔥 Suppression des fichiers .mp3 générés par l'IA
Write-Host "🧹 Suppression des fichiers audio générés (.mp3)..."
Get-ChildItem -Path . -Filter "output_*.mp3" -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue


Write-Host "✅ Tous les processus terminés."
