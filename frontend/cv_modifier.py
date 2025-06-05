# cv_modifier.py

from fpdf import FPDF
import datetime
import os

def generate_modified_cv_pdf(cv_text: str, suggestions: str, updated_cv_text: str, score: int) -> str:
    """
    Génére un PDF à partir du CV réécrit (`updated_cv_text`), 
    en ajoutant le score en en-tête.
    Retourne le chemin absolu du fichier PDF généré.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cv_revisité_{timestamp}.pdf"
    output_path = os.path.join(os.getcwd(), filename)

    # Initialisation FPDF avec marges
    pdf = FPDF(format="A4", unit="mm")
    margin = 10
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_left_margin(margin)
    pdf.set_right_margin(margin)

    # 1) Afficher le score en en-tête (Arial B, taille 14)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Score CV : {score}/100", ln=True, align="C")
    pdf.ln(5)

    # 2) Normaliser la police pour le reste du CV
    pdf.set_font("Arial", size=11)
    epw = pdf.w - pdf.l_margin - pdf.r_margin  # largeur effective

    # 3) Parcourir chaque ligne du CV réécrit et l'insérer
    for line in updated_cv_text.splitlines():
        # Eviter lignes vides ou trop longues
        pdf.multi_cell(epw, 6, line)

    # 4) Sauvegarder le PDF
    pdf.output(output_path)
    return output_path
