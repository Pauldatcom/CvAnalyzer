import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="🚀 Lancer mon parcours", layout="wide")

# 1) Injection du CSS global (style.css) pour l’ensemble de l’application :
#    - Masque les conteneurs vides de Streamlit (pour éviter marges/fond blancs).
#    - Charge votre feuille de style (header, footer, boutons, etc.).


style_path = os.path.join(os.path.dirname(__file__), "..", "style.css")

if os.path.exists(style_path):
    with open(style_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



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
