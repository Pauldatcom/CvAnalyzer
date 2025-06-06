# """
# server.py – Serveur FastAPI pour l’entretien vocal et le backend IA.
# - /context (POST) :
#     • Reçoit en JSON : { "cv_text", "offer_text", "analysis_text", "updated_cv_text" }.
#     • Stocke ces données dans des variables globales ou en session.
#     • Réinitialise conversation_history et conversation_state.
# - /reset (GET) :
#     • Réinitialise l’historique de l’entretien (questions/réponses) côté serveur.
#     • Remet conversation_state à « questions » et num_question à 0.
# - /transcribe (POST) :
#     • Reçoit un fichier audio (UploadFile).
#     • Sauvegarde temporairement l’audio WAV/MP3.
#     • Convertit en WAV mono 16 kHz (ffmpeg).
#     • Utilise Whisper (openai.whisper) pour transcrire l’audio en texte.
#     • Construit un prompt contextualisé pour Mistral (CV, offre, analyse, CV modifié).
#     • Si conversation_state == “questions” et num_question < 3 :
#     #     • Demander à Mistral de poser la n+1-ème question RH.
#     #   Sinon, passer en mode “bilan” pour générer un feedback final.
#     • Convertit la réponse Mistral en MP3 via edge-tts (par segments de 600 caractères si nécessaire).
#     • Supprime les fichiers temporaires et renvoie {"audio_url", "text"} au front-end.
# - /audio/{filename} (GET) :
#     • Sert un fichier MP3 généré (pour que la balise <audio> puisse le lire).
# """

# Middleware CORS pour autoriser localhost:8501 (Streamlit) à appeler fastapi (sur le port 8000).
# shared_context regroupe CV, offre, analyse, CV modifié, partagé entre /context et /transcribe.
# conversation_history stocke l’historique Q/R coté serveur.
# conversation_state et num_question gèrent la logique “3 questions” puis “bilan”.
# Whisper est chargé à chaque appel, mais on peut optimiser en le chargeant une seule fois au démarrage.
# edge-tts découpe le texte pour rester <600 caractères (limite du service).
# Les fichiers temporaires sont systématiquement nettoyés (sécurité, espace disque).




from playwright_scraper import extract_job_posting 
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import uuid
import whisper
import os
import subprocess
from mistralai import Mistral
from dotenv import load_dotenv
import time
import glob



load_dotenv()

model = whisper.load_model("base")
mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
ffmpeg_exec = os.getenv("FFMPEG_PATH", "ffmpeg")

app = FastAPI()


@app.post("/scrape")
async def scrape_offer(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return {"error": "URL manquante"}
    
    try:
        result = await extract_job_posting(url)
        return result
    except Exception as e:
        return {"error": f"Erreur Playwright : {str(e)}"}
    
from fastapi import Request

@app.post("/extract_job")
async def extract_job(request: Request):
    from playwright_scraper import extract_job_posting
    import asyncio

    data = await request.json()
    url = data.get("url")
    if not url:
        return {"error": "URL manquante"}
    try:
        job = await extract_job_posting(url)
        return job
    except Exception as e:
        return {"error": str(e)}



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

shared_context = {}
conversation_history = []
conversation_state = {
    "num_question": 0,
    "mode": "questions"
}
_MAX_AGE_SECONDS = 600



def delete_old_temp_files():
    """
    Supprime tous les fichiers temp_*.wav à la racine et
    static/output_*.mp3 de plus de 10 minutes.
    """
    now = time.time()
       # 1) temp_*.wav à la racine
    for wav_file in glob.glob("temp_*.wav"):
        try:
            if now - os.path.getmtime(wav_file) > _MAX_AGE_SECONDS:
                os.remove(wav_file)
        except FileNotFoundError:
            pass

    # 2) output_*.mp3 dans static/
    for mp3_file in glob.glob(os.path.join("static", "output_*.mp3")):
        try:
            if now - os.path.getmtime(mp3_file) > _MAX_AGE_SECONDS:
                os.remove(mp3_file)
        except FileNotFoundError:
            pass

    # 3) output_*.wav à la racine
    for wav_file in glob.glob("output_*.wav"):
        try:
            if now - os.path.getmtime(wav_file) > _MAX_AGE_SECONDS:
                os.remove(wav_file)
        except FileNotFoundError:
            pass

    # 4) converted_*.wav à la racine
    for wav_file in glob.glob("converted_*.wav"):
        try:
            if now - os.path.getmtime(wav_file) > _MAX_AGE_SECONDS:
                os.remove(wav_file)
        except FileNotFoundError:
            pass

@app.post("/context")
async def store_context(request: Request):
    global shared_context, conversation_history, conversation_state
    shared_context = await request.json()
    conversation_history = []
    conversation_state = {"num_question": 0, "mode": "questions"}
    return {"status": "ok"}

@app.post("/reset")
async def reset_history():
    global conversation_history, conversation_state
    conversation_history = []
    conversation_state = {"num_question": 0, "mode": "questions"}
    return {"status": "history cleared"}

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    
    temp_filename = f"temp_{uuid.uuid4().hex}.wav"
    converted_filename = os.path.abspath(f"static/output_{uuid.uuid4().hex}.mp3")

    with open(temp_filename, "wb") as f:
        f.write(await audio.read())

    wav_filename = converted_filename.replace(".mp3", ".wav")
    subprocess.run([
        ffmpeg_exec, "-y", "-i", temp_filename,
        "-ar", "16000", "-ac", "1", "-f", "wav", wav_filename
    ], check=True)

    transcription = model.transcribe(wav_filename)["text"]
    print("🖍️ Transcription :", transcription)

    global conversation_history, conversation_state

    contextual_prompt = f"""
Tu es un recruteur RH simulant un entretien d'embauche.

Contexte :
- CV : {shared_context.get("cv", "")[:1000]}
- Offre : {shared_context.get("offer", "")[:1000]}
- Analyse IA : {shared_context.get("analysis", "")[:1000]}
- CV modifié : {shared_context.get("updated", "")[:1000]}
"""

    messages = [{"role": "system", "content": contextual_prompt}] + conversation_history
    messages.append({"role": "user", "content": transcription})

    conversation_history.append({"role": "user", "content": transcription})

    if conversation_state["mode"] == "questions":
        if conversation_state["num_question"] < 3:
            messages.append({
                "role": "system",
                "content": f"Pose une question RH pertinente, adaptée au poste, sans commenter. C'est la question {conversation_state['num_question'] + 1} sur 3."
            })
            response = mistral.chat.complete(model="mistral-large-latest", messages=messages)
            answer = response.choices[0].message.content.strip()
            conversation_state["num_question"] += 1
            conversation_history.append({"role": "assistant", "content": answer})
        else:
            conversation_state["mode"] = "bilan"
            answer = "Merci pour vos réponses. Voici une synthèse vocale de votre entretien."
    else:
        # Synthèse finale
        bilan_prompt = contextual_prompt + "\nVoici les réponses du candidat :\n"
        for msg in conversation_history:
            if msg["role"] == "user":
                bilan_prompt += f"- {msg['content']}\n"
        bilan_prompt += "\nDonne un retour RH global en 4 phrases maximum."
        response = mistral.chat.complete(model="mistral-large-latest", messages=[{"role": "system", "content": bilan_prompt}])
        answer = response.choices[0].message.content.strip()
        conversation_state["mode"] = "fini"

    # Nettoyage texte pour edge-tts
    tts_text = answer.replace('"', "'").replace("**", "").replace("\n", " ").strip()[:600]
    tts_command = f'edge-tts --text "{tts_text}" --write-media "{converted_filename}"'
    print("🔊 Commande TTS:", tts_command)
    os.system(tts_command)

    os.remove(temp_filename)
    os.remove(wav_filename)

    return {"audio_url": f"http://localhost:8000/audio/{os.path.basename(converted_filename)}", "text": answer}

@app.get("/audio/{filename}")
def serve_audio(filename: str):
    path = f"static/{filename}"
    if not os.path.exists(path):
        return {"error": "Fichier audio introuvable."}
    return FileResponse(path, media_type="audio/mpeg", filename=filename)
