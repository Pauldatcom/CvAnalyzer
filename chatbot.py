# app.py

import os
import streamlit as st
from mistralai import Mistral
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-large-latest"
client = Mistral(api_key=api_key)

# Configuration de la page
st.set_page_config(page_title="Chatbot Mistral", layout="centered")
st.title("🤖 Chatbot IA avec mémoire (Mistral)")

# Initialiser l'historique si nécessaire
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "system", "content": "Vous êtes un RH expert dans les métiers de la data et vous savez répondre aux questions sur les CV et les fiches de poste."}]

# Afficher l'historique des messages
for index, msg in enumerate(st.session_state.chat_history):
    if index != 0 :
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Entrée utilisateur
if prompt := st.chat_input("Pose une question à l'IA..."):
    # Afficher le message utilisateur
    st.chat_message("user").markdown(prompt)

    # Ajouter à l'historique
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Appeler l'API Mistral
    try:
        response = client.chat.complete(
            model=model,
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Erreur lors de l'appel à l'API : {e}"

    # Afficher la réponse IA
    st.chat_message("assistant").markdown(answer)

    # Ajouter la réponse à l'historique
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
