import streamlit as st
from parser import extract_text
import os
import subprocess
import json
import sys
import chardet
import base64
from dotenv import load_dotenv

from groq_analyzer import analyze_cv_and_offer, generate_updated_cv, score_cv
from cv_modifier import generate_modified_cv_pdf

load_dotenv()

st.set_page_config(page_title="CV & Offre Optimizer", layout="wide")

# -------------------------------------------------------------------
# Page 1 – « Analyse IA du profil »
# - Permet à l’utilisateur d’uploader un CV (PDF/TXT) et de coller l’URL d’une offre.
# - Lance job_runner.py pour extraire la fiche de poste (Playwright).
# - Appelle Groq (LLaMA 3) pour analyser l’écart CV vs. offre, suggérer des améliorations.
# - Affiche score de compatibilité, suggestions, et génère un CV réécrit (PDF).
# -------------------------------------------------------------------


# =============================================================================
# 2) Upload du CV :
#    - st.file_uploader(accept_multiple_files=False, type=["pdf","txt"])
#    - Extraction du texte brut avec parser.extract_text (ou pdfplumber)
#    - Stocker le texte dans st.session_state["cv_text"] pour réutilisation.
# =============================================================================

# =============================================================================
# 3) Champ pour saisir/coller l’URL de l’offre d’emploi :
#    - st.text_input("URL de l’offre", key="job_url")
#    - Vérifier que l’URL n’est pas vide avant de lancer l’analyse.
# =============================================================================



# =============================================================================
# 4) Bouton “Démarrer l’analyse” :
#    - Au clic :
#       • Exécute job_runner.py via subprocess.run(["python", "job_runner.py", url])
#         pour récupérer la fiche de poste (JSON).
#       • Parse JSON en dict Python (json.loads).
#       • Si erreur, afficher un message d’erreur.
#       • Afficher métadonnées de l’offre (titre, entreprise, lieu).
#       • Appeler analyze_cv_and_offer(cv_text, offer_text) (module groq_analyzer).
#           – Affiche “Analyse en cours…” pendant l’appel.
#       • Afficher les suggestions IA (listes d’écarts, points à améliorer).
#       • Calculer score de compatibilité via score_cv(cv_text, offer_text).
#       • Afficher le score (par exemple en % ou en note sur 100).
# =============================================================================

# =============================================================================
# 5) Génération du CV mis à jour :
#    - Appeler generate_updated_cv(cv_text, suggestions) pour réécrire le CV.
#    - Générez un PDF avec generate_modified_cv_pdf(updated_cv_text, score).
#    - Proposer un bouton st.download_button pour télécharger le PDF.
# =============================================================================

# =============================================================================
# 6) Avertissement RGPD :
#    - Informer que le CV (données personnelles) est envoyé à une API externe (Groq).
#    - Inviter à lire la politique de confidentialité / supprimer son CV après usage.
# =============================================================================



# 1) Titre de la page
st.title("🧑‍💼 Optimiseur de CV & Offres d'emploi")

# 2) Injection du CSS principal (sur UNE seule ligne pour éviter bloc visible)
if os.path.exists("frontend/style.css"):
    with open("frontend/style.css", "r") as f:
        css_content = f.read()
    # Injecte le CSS complet
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    # Masque le conteneur vide créé autour de ce <style>
    st.markdown(
        "<style>[data-testid='stElementContainer']:has(style) {display:none !important;}</style>",
        unsafe_allow_html=True,
    )

# 3) Barre latérale : upload du CV
st.sidebar.header("1. Charger votre CV")
uploaded_cv = st.sidebar.file_uploader("Importer un CV (.pdf)", type=["pdf"])
if uploaded_cv:
    ext = os.path.splitext(uploaded_cv.name)[1]
    orig_temp_path = f"cv_temp{ext}"
    with open(orig_temp_path, "wb") as f:
        f.write(uploaded_cv.read())
    try:
        st.session_state.cv_text = extract_text(orig_temp_path)
        st.session_state.orig_pdf = orig_temp_path
    except Exception as e:
        st.error(f"Erreur d'extraction du CV : {e}")
        st.session_state.cv_text = ""

# 4) Barre latérale : lien de l'offre
st.sidebar.header("2. Lien de l'offre d'emploi")
job_url = st.sidebar.text_input("Coller ici le lien de l'offre (Welcome to the Jungle, etc.)")

# 5) Bouton Démarrer l’analyse
if job_url and uploaded_cv and st.sidebar.button("🚀 Démarrer l'analyse"):
    try:
        st.session_state.cv_text = extract_text(st.session_state.orig_pdf)
    except Exception as e:
        st.error(f"Erreur lecture CV : {e}")
        st.session_state.cv_text = ""

    try:
        process = subprocess.run(
            [sys.executable, "job_runner.py", job_url],
            timeout=60,
            capture_output=True,
        )
        encoding = chardet.detect(process.stdout)["encoding"] or "utf-8"
        raw = process.stdout.decode(encoding).strip().replace("\u2019", "'").replace("\xa0", " ")
        result = json.loads(raw)
    except subprocess.TimeoutExpired:
        st.error("Temps dépassé lors de l'extraction.")
        result = {"error": "Timeout"}
    except Exception as e:
        st.error(f"Erreur extraction offre : {e}")
        result = {"error": str(e)}

    if result and not result.get("error"):
        st.session_state.offer_text = result.get("description", "")
        st.session_state.offer_title = result.get("title", "")
        st.session_state.offer_company = result.get("company", "")
        st.session_state.offer_location = result.get("location", "")

        st.success("✅ Analyse terminée")
        with st.expander("📄 Aperçu du CV original"):
            with open(st.session_state.orig_pdf, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_view = (
                    f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
                    f'width="700" height="900"></iframe>'
                )
                st.markdown(pdf_view, unsafe_allow_html=True)

        st.write(f"**Poste :** {st.session_state.offer_title}  ")
        st.write(f"**Entreprise :** {st.session_state.offer_company}  ")
        st.write(f"**Lieu :** {st.session_state.offer_location}")

        with st.spinner("Analyse IA avec LLaMA 3 en cours..."):
            try:
                st.session_state.llama_analysis = analyze_cv_and_offer(
                    st.session_state.cv_text,
                    st.session_state.offer_text,
                )
            except Exception as e:
                st.error(f"Erreur analyse IA : {e}")
                st.session_state.llama_analysis = None

# 6) Affichage des résultats IA
if "llama_analysis" in st.session_state and st.session_state.llama_analysis:
    st.subheader("📌 Nos recommandations")
    st.markdown(st.session_state.llama_analysis)

    with st.spinner("Calcul du score de compatibilité..."):
        try:
            st.session_state.cv_score = score_cv(
                st.session_state.cv_text,
                st.session_state.offer_text,
            )
        except Exception as e:
            st.error(f"Erreur score : {e}")
            st.session_state.cv_score = 0

    st.write(f"**Score de compatibilité du CV :** {st.session_state.cv_score}/100")

    with st.spinner("Réécriture intelligente du CV..."):
        try:
            updated_cv = generate_updated_cv(
                st.session_state.cv_text,
                st.session_state.llama_analysis,
            )
        except Exception as e:
            st.error(f"Erreur lors de la réécriture : {e}")
            updated_cv = None

    if updated_cv:
        st.subheader("✏️ CV mis à jour par l'IA")
        st.text_area("CV revisité", updated_cv, height=350)

        try:
            pdf_path = generate_modified_cv_pdf(
                st.session_state.cv_text,
                st.session_state.llama_analysis,
                updated_cv,
                st.session_state.cv_score,
            )
            with open(pdf_path, "rb") as f:
                b64_pdf = base64.b64encode(f.read()).decode("utf-8")
            os.remove(pdf_path)

            st.markdown("#### Visualisation du CV modifié :")
            pdf_view = (
                f'<iframe src="data:application/pdf;base64,{b64_pdf}" '
                f'width="700" height="900"></iframe>'
            )
            st.markdown(pdf_view, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erreur PDF : {e}")

# 7) Avertissement RGPD
st.markdown(
    """
---
<div style='font-size: 0.9em; color: gray;'>
⚠️ En lançant l'analyse, vous acceptez que les informations de votre CV et de l'offre soient transmises à LLaMA 3 pour traitement via Groq. Aucun stockage local n'est effectué, mais les données transitent par une API externe.
</div>
""",
    unsafe_allow_html=True,
)
