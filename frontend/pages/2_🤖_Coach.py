import streamlit as st
from mistralai import Mistral
import os
from dotenv import load_dotenv
import urllib.parse

# Chargement des variables d'environnement
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-large-latest"
client = Mistral(api_key=api_key)

st.set_page_config(page_title="Assistant RH IA", layout="wide")
st.title("🤖 Assistant RH contextuel & Offres personnalisées")




# =============================================================================
# 1) Docstring en tête :
#    """
#    Page 2 – Coach RH contextuel :
#    - Charge le contexte complet depuis st.session_state : 
#         cv_original, cv_modifié, fiche_de_poste, analyse_LLaMA.
#    - Initialise l’historique du chat (st.session_state["chat_history"]).
#    - À chaque message utilisateur, envoie le contexte + chat_history à Mistral.
#    - Affiche la réponse IA et met à jour st.session_state["chat_history"].
#    - En bas, propose des liens vers des offres similaires.
#    """
# =============================================================================

# =============================================================================
# 2) Chargement du contexte :
#    - if "cv_modified" in st.session_state: afficher le texte du CV modifié.
#    - Sinon, demander à l’utilisateur de revenir sur la page 1 pour générer le CV.
# =============================================================================

# =============================================================================
# 3) Zone de chat :
#    - st.chat_input() pour le message utilisateur.
#    - Quand l’utilisateur envoie un message :
#       • Construire le prompt Mistral : system + contexte (CV orig., CV mod., offre, analyse).
#       • Appeler mistralai.chat(messages=…, temperature=…).
#       • Afficher la réponse IA avec st.chat_message(role="assistant", …).
#       • Conserver l’historique dans st.session_state["chat_history"].
# =============================================================================

# =============================================================================
# 4) Suggestions de liens d’offres externes :
#    - À partir du titre du poste, générer un lien Google/Indeed/LinkedIn vers des offres similaires.
#    - Ex. :
#         st.markdown(f"[Voir d’autres offres {job_title} sur LinkedIn](https://www.linkedin.com/jobs/search?keywords={job_title})")
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

# ------------------ CONTEXTE POUR LE CHAT ------------------

cv = st.session_state.get("cv_text", "")
cv_updated = st.session_state.get("updated_cv_text", "")
offer = st.session_state.get("offer_text", "")
llama_analysis = st.session_state.get("llama_analysis", "")

system_msg = f"""
Tu es un recruteur expert. Voici le contexte :
- CV original : {cv[:1000]}
- CV modifié par l'IA : {cv_updated[:1000]}
- Fiche de poste : {offer[:1000]}
- Analyse LLaMA 3 : {llama_analysis[:1500]}

Réponds comme un recruteur : explique, conseille, reformule, anticipe les questions d'entretien.
"""

# ------------------ AFFICHAGE DU CV MODIFIÉ ------------------

if cv_updated:
    st.subheader("✏️ CV mis à jour par l'IA")
    st.text_area("CV réécrit", cv_updated, height=300)

# ------------------ CHATBOT RH ------------------

st.subheader("💬 Discuter avec l'IA RH")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "system", "content": system_msg}]

for msg in st.session_state.chat_history[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Posez votre question à l'assistant RH..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    try:
        response = client.chat.complete(model=model, messages=st.session_state.chat_history)
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Erreur API : {e}"

    st.chat_message("assistant").markdown(reply)
    st.session_state.chat_history.append({"role": "assistant", "content": reply})


# ------------------ RECHERCHE D'OFFRES BASÉE SUR LA FICHE DE POSTE ------------------

st.divider()

with st.expander("🔍 Voir les offres recommandées"):
    if offer:
        titre_poste = st.session_state.get("offer_title", "data")
        query = urllib.parse.quote_plus(titre_poste.strip())

        st.markdown(
            f"🔗 [Voir toutes les offres]"
            f"(https://www.welcometothejungle.com/fr/jobs?query={query})"
        )

        st.markdown("### 🎯 Offres recommandées :")
        st.markdown(f"- [🔗 Welcome to the Jungle](https://www.welcometothejungle.com/fr/jobs?query={query})")
        st.markdown(f"- [🔗 LinkedIn Jobs](https://www.linkedin.com/jobs/search/?keywords={query})")
        st.markdown(f"- [🔗 Indeed France](https://fr.indeed.com/jobs?q={query})")
        st.markdown(
            f"- [🔗 Glassdoor]"
            f"(https://www.glassdoor.fr/Emploi/{query}-emplois-SRCH_KO0,{len(query)}.htm)"
        )
        st.markdown(f"- [🔗 Jooble](https://fr.jooble.org/SearchResult?ukw={query})")
    else:
        st.warning("Veuillez analyser une fiche de poste dans la page précédente pour voir les offres recommandées.")
