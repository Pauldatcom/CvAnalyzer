import streamlit as st
import streamlit.components.v1 as components
from jose import jwt
import time
from fpdf import FPDF
import io
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LIVEKIT_API_KEY", "mykey")
api_secret = os.getenv("LIVEKIT_API_SECRET", "mysecret")
room_name = "entretiens"
livekit_url = os.getenv("LIVEKIT_URL", "ws://localhost:7880/rtc")

st.set_page_config(page_title="🖙️ Assistant vocal RH", layout="centered")
st.title("🖙️ Simulateur d’entretien vocal")



# -------------------------------------------------------------------
# Page 3 – « Entretien vocal »
# - Génère un token JWT pour LiveKit (via generate_token.py) à partir d’un ID utilisateur.
# - Permet de rejoindre une room vocal/vidéo en temps réel (LiveKit JS SDK).
# - Enregistre le micro, envoie l’audio au backend (/transcribe) via JavaScript fetch.
# - Backend utilise Whisper pour transcrire, Mistral pour générer questions/réponses,
#   puis edge-tts pour synthétiser la réponse vocale (MP3).
# - Affiche lecteur audio pour écouter la réponse, garde l’historique Q/R en local.


# =============================================================================
# 2) Docstring en tête :
#    """
#    Page 3 – Simulateur d’entretien vocal :
#    - Input pour identifiant (identity) afin de personnaliser le JWT LiveKit.
#    - Bouton “Générer le token” :
#         • Charge les variables d’environnement LIVEKIT_API_KEY, LIVEKIT_API_SECRET.
#         • Construit le JWT HMAC SHA256 (payload : iss, sub, roomJoin rights, exp=+1h).
#         • Envoie le contexte global (CV, offre, analyse, CV modifié) au backend (/context).
#    - Chargement du SDK LiveKit (livekit.umd.min.js) et JS pour join la room.
#    - Boutons “Rejoindre la salle” & “Quitter la salle” :
#         • Connecte à la room, publie le micro.
#         • StartRecording() pour récupérer le MediaStream du micro.
#    - StartRecording / StopRecording (JS/Streamlit Bidirectionnel) :
#         • Envoie un Blob audio au endpoint FastAPI (/transcribe).
#         • Récupère JSON { audio_url:…, text:… }.
#         • Affiche un lecteur audio HTML <audio src="…"> pour la réponse IA.
#         • Mémorise Q/R dans st.session_state["interview_history"].
#    - Bouton “Générer le compte-rendu” :
#         • Parcourt interview_history, génère un PDF via FPDF (questions + réponses).
#         • Propose st.download_button pour télécharger le PDF final.
#    """
# =============================================================================

# =============================================================================
# 3) Chargement des variables d’environnement :
#    - LIVEKIT_API_KEY, LIVEKIT_API_SECRET (python-dotenv).
#    - Vérifier que la clé et le secret existent, sinon st.error(…).
# =============================================================================

# =============================================================================
# 4) Génération du JWT LiveKit :
#    - Construire payload = { "iss": LIVEKIT_API_KEY, "sub": identity, "room": "entretiens", "exp": <timestamp> }.
#    - Utiliser jose.jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256").
#    - Afficher le token à l’écran ou le stocker dans st.session_state["lk_token"].
#    - Appeler fetch("/context", method="POST", body=JSON.stringify({...})) pour transmettre
#      CV + offre + analyse + cv_modifié au backend.
# =============================================================================

# =============================================================================
# 5) Chargement du SDK LiveKit JS :
#    - components.html("""<script src="static/livekit.umd.min.js"></script> …""", height=…)  
#    - Code JavaScript pour initialiser LiveKit Connect, rejoindre la room, surveiller participants.
# =============================================================================

# =============================================================================
# 6) Boutons d’enregistrement :
#    - “Start Recording” → JS obtient MediaStream du navigateur, enregistre sur le micro.
#    - Lorsque l’utilisateur clique “Stop Recording” → envoie le Blob au serveur via fetch("/transcribe").
#    - Récupérer la réponse JSON { audio_url, text },  
#         • Afficher la transcription texte avec st.write ou st.chat_message,
#         • Afficher le lecteur audio MP3 (st.audio(info["audio_url"])).
#    - Ajouter chaque Q/R dans st.session_state["interview_history"].
# =============================================================================

# =============================================================================
# 7) Génération du compte-rendu PDF :
#    - À la fin de l’entretien (ou sur demande), prendre interview_history (liste de dicts).
#    - Créer un PDF avec FPDF :
#         • Titre « Compte‐rendu d’entretien », date/heure, nom du candidat.
#         • Lister chaque question / réponse sous forme de texte.
#    - Stocker le PDF dans un tempdir local (par ex. `/tmp`),  
#      l’encode en base64 et proposer st.download_button pour le fichier.
#    - Supprimer le fichier temporaire après envoi.
# =============================================================================

# ------------------ Injection du CSS (sans bloc vide) ------------------
if os.path.exists("frontend/style.css"):
    with open("frontend/style.css", "r") as f:
        css_content = f.read()
    # Injecte le CSS complet sur une seule ligne pour éviter un bloc Markdown vide
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    # Cache le conteneur que Streamlit pourrait créer autour de ce <style>
    st.markdown(
        "<style>[data-testid='stElementContainer']:has(style) {display: none !important;}</style>",
        unsafe_allow_html=True,
    )

# ------------------ Historique d'entretien ------------------
if "entretien_history" not in st.session_state:
    st.session_state.entretien_history = []

# ------------------ Fonction de génération du PDF ------------------
def generate_transcript_pdf(history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Compte-rendu de l'entretien vocal", ln=True, align="C")
    pdf.ln(10)
    for i, item in enumerate(history, 1):
        pdf.multi_cell(0, 10, f"{i}. Question : {item['question']}\n   Réponse IA : {item['reponse']}\n")
        pdf.ln(4)
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# ------------------ Saisie identifiant ------------------
identity = st.text_input("Identifiant (ex: candidat001)", value="candidat001")

# ------------------ Génération du token JWT ------------------
if st.button("🎫 Générer le token JWT"):
    payload = {
        "iss": api_key,
        "sub": identity,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "video": {"roomJoin": True, "room": room_name}
    }
    requests.post("http://localhost:8000/cleanup_temp") 
    token = jwt.encode(payload, api_secret, algorithm="HS256")
    st.session_state["livekit_token"] = token
    st.success("✅ Token généré et prêt à l'emploi")
    try:
        requests.post("http://localhost:8000/context", json={
            "cv": st.session_state.get("cv_text", ""),
            "offer": st.session_state.get("offer_text", ""),
            "analysis": st.session_state.get("llama_analysis", ""),
            "updated": st.session_state.get("updated_cv_text", "")
        })
    except:
        st.warning("🔴 Impossible de transmettre le contexte à l'API.")

# ------------------ Chargement du SDK LiveKit ------------------
try:
    with open("static/livekit.umd.min.js", "r", encoding="utf-8") as f:
        sdk_js = f.read()
except:
    sdk_js = ""
    st.error("❌ Fichier SDK LiveKit manquant.")

# ------------------ Interface LiveKit ------------------
if "livekit_token" in st.session_state and sdk_js:
    components.html(f"""
    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
    <script type="module" src="https://cdn.jsdelivr.net/npm/livekit-client/dist/livekit-client.umd.min.js"></script>

    <div class='container mt-4'>
        <div id='status' class='text-muted mb-2'>Non connecté</div>
        <button class='btn btn-outline-primary mb-2' onclick='connectLiveKit()'>🎤 Rejoindre la salle</button>
        <div id='timer' class='fw-bold mt-3 mb-2'></div>
        <button class='btn btn-success' id='startBtn' onclick='startRecording()'>🎙️ Démarrer</button>
        <button class='btn btn-danger mt-2' id='stopBtn' onclick='stopRecording()' style='display:none;'>⏹️ Arrêter</button>
        <audio id='response-audio' controls style='display:none; margin-top: 20px;'></audio>
        <div id='mic-alert' class='alert alert-danger mt-3' style='display:none;'>🎙️ Micro non autorisé ou erreur de permission. Vérifiez votre navigateur.</div>
    </div>
    <script>
        let mediaRecorder;
        let audioChunks = [];
        let secondsElapsed = 0;
        let countdown;

        window.addEventListener("load", function() {{
            var client = window.LivekitClient || window.LiveKit || (window.LivekitClient && window.LivekitClient.default);
            if (!client) {{
                document.getElementById("status").innerText = "❌ SDK LiveKit non chargé.";
                console.error("❌ LiveKit SDK non accessible.");
            }} else {{
                console.log("✅ SDK LiveKit détecté :", client);
                window.clientLiveKit = client;
                LiveKitLoaded = true;
            }}
        }});

        async function connectLiveKit() {{
            try {{
                const token = "{st.session_state['livekit_token']}";
                const url = "{livekit_url}";
                console.log("🔑 Token utilisé :", token);
                console.log("🌐 Connexion à :", url);
                const room = new LivekitClient.Room();

                console.log("✅ Connecté !", room);
                document.getElementById("status").innerText = "✅ Connecté à la salle";
            }} catch (err) {{
                console.error("❌ Connexion échouée :", err);
                document.getElementById("status").innerText = "❌ Connexion échouée : " + err.message;
            }}
        }}

        async function startRecording() {{
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                secondsElapsed = 0;
                document.getElementById("startBtn").style.display = "none";
                document.getElementById("stopBtn").style.display = "inline-block";
                countdown = setInterval(() => {{
                    secondsElapsed++;
                    document.getElementById("timer").innerText = `🎤 Enregistrement : ${{secondsElapsed}}s...`;
                }}, 1000);
                mediaRecorder.ondataavailable = event => {{
                    if (event.data.size > 0) audioChunks.push(event.data);
                }};
                mediaRecorder.onstop = async () => {{
                    clearInterval(countdown);
                    document.getElementById("timer").innerText = "⏹️ Traitement...";
                    const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
                    const formData = new FormData();
                    formData.append("audio", audioBlob, "voice.wav");
                    try {{
                        const response = await fetch("http://localhost:8000/transcribe", {{ method: "POST", body: formData }});
                        const result = await response.json();
                        const audioUrl = result.audio_url;
                        const audioPlayer = document.getElementById("response-audio");
                        audioPlayer.src = audioUrl;
                        audioPlayer.style.display = "block";
                        audioPlayer.play();
                    }} catch (error) {{
                        document.getElementById("mic-alert").innerText = "❌ Erreur de traitement ou serveur indisponible.";
                        document.getElementById("mic-alert").style.display = "block";
                    }}
                    document.getElementById("timer").innerText = "";
                    document.getElementById("startBtn").style.display = "inline-block";
                    document.getElementById("stopBtn").style.display = "none";
                }};
                mediaRecorder.start();
            }} catch (err) {{
                document.getElementById("mic-alert").style.display = "block";
            }}
        }}

        function stopRecording() {{
            if (mediaRecorder && mediaRecorder.state === "recording") mediaRecorder.stop();
        }}
    </script>
    """, height=600)

# ------------------ Bouton pour voir le compte-rendu ------------------
if st.button("🗞️ Voir le compte-rendu de l'entretien"):
    st.markdown("### Compte-rendu de la session")
    for i, pair in enumerate(st.session_state.entretien_history, 1):
        st.markdown(f"**{i}.** 🎤 *{pair['question']}*")
        st.markdown(f"   🧠 *{pair['reponse']}*")
        st.markdown("---")
    pdf_file = generate_transcript_pdf(st.session_state.entretien_history)
    b64 = base64.b64encode(pdf_file.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="compte_rendu_entretien.pdf">📄 Télécharger le compte-rendu en PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
