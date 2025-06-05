import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="🚀 Lancer mon parcours", layout="wide")

# 1) Injection du CSS global (style.css) pour l’ensemble de l’application :
#    - Masque les conteneurs vides de Streamlit (pour éviter marges/fond blancs).
#    - Charge votre feuille de style (header, footer, boutons, etc.).

# 1) Charge le contenu du fichier style.css dans une variable
with open("style.css", "r") as f:
    css_content = f.read()

# 2) Injecte le CSS dans la page, sur UNE SEULE LIGNE, sans aucun espace ou retour à la ligne avant "<style>"
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# 3) Cache également le conteneur invisible créé par Streamlit autour de tout <style>
st.markdown("<style>[data-testid='stElementContainer']:has(style) {display: none !important;}</style>", unsafe_allow_html=True)



# 4) Maintenant, ton HTML « header + hero + footer » est injecté normalement :
st.markdown(
    """
    <!-- Header -->
    <div class="header">
        <h2>CareerBoost</h2>
        <a href="mailto:contact@careerboost.ai">Nous contacter</a>
    </div>

    <!-- Hero Section -->
    <div class="main-container">
        <h1>Démarrez votre parcours professionnel</h1>
        <p class="subtitle">
            Votre copilote IA pour optimiser votre CV, simuler des entretiens,
            et trouver les meilleures opportunités de carrière.
        </p>
    </div>

   
    """,
    unsafe_allow_html=True,
)

# 5) liens de navigation
col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/1_📊_Analyse_IA_du_profil.py", label="🔍 Analyser une offre", icon="🔍")
with col2:
    st.page_link("pages/3_🗣️_Entretien_vocal.py", label="🎧 Simulateur vocal", icon="🎧")
    st.page_link("pages/2_🤖_Coach.py", label="💼 Offres recommandées", icon="💼")

# 6) Le logo en sidebar
logo_path = "ImageProjetPython.jpeg"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.sidebar.image(logo, width=100)

# 7) Enfin, on supprime les éventuels espaces/marges vides générés par Streamlit dans la structure
st.markdown(
    "<style>"
    "section.main > div:has(.main-container) > div:first-child {display: none !important;}"
    "section.main > div:has(.main-container) > div:nth-child(2) {display: none !important;}"
    "section.main > div {padding-top: 0rem !important;}"
    "</style>",
    unsafe_allow_html=True,
)
