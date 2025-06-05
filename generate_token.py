from jose import jwt
import time
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LIVEKIT_API_KEY")
api_secret = os.getenv("LIVEKIT_API_SECRET")
room_name = "entretiens"
identity = "candidat001"

# """
# Script standalone pour générer un JWT LiveKit.
# - Récupère LIVEKIT_API_KEY et LIVEKIT_API_SECRET depuis .env (via python-dotenv).
# - Construit un token HMAC SHA256 autorisant la création et la participation à une room « entretiens ».
# - Affiche le token dans la console (stdout) et le copie dans st.session_state si appelé depuis Streamlit.
# """


# JWT payload attendu par LiveKit
payload = {
    "iss": api_key,
    "sub": identity,
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600,  # expire dans 1h
    "video": {
        "create": True,
        "roomJoin": True,
        "room": room_name
    }
}

# Signature en HMAC SHA256
token = jwt.encode(payload, api_secret, algorithm="HS256")

print("✅ Token JWT généré :")
print(token)
