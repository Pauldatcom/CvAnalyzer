# parser.py

import pdfplumber
from pathlib import Path

def parse_pdf(file_path: str) -> str:
    """
    Ouvre le PDF avec pdfplumber et restitue le texte page par page,
    en conservant les sauts de ligne (évite de scinder les mots).
    """
    text_pages = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)
    # On joint toutes les pages avec deux sauts de ligne entre chaque
    return "\n\n".join(text_pages).strip()

def parse_txt(file_path: str) -> str:
    """
    Tente plusieurs encodages pour lire un fichier .txt.
    Si on détecte un PDF déguisé (signature %PDF), on lève une erreur.
    """
    for encoding in ("utf-8", "latin-1", "iso-8859-1"):
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
                if content.lstrip().startswith("%PDF"):
                    raise ValueError("Le fichier semble être un PDF, mais a une extension .txt.")
                return content.strip()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("Impossible de lire le fichier texte avec les encodages connus.")

def extract_text(file_path: str) -> str:
    """
    Selon l’extension ou la signature, appelle parse_pdf ou parse_txt.
    """
    ext = Path(file_path).suffix.lower()

    # On vérifie la signature binaire pour PDF
    with open(file_path, "rb") as f:
        signature = f.read(4)

    if signature == b"%PDF":
        return parse_pdf(file_path)
    elif ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".txt":
        return parse_txt(file_path)
    else:
        raise ValueError(f"Format de fichier non supporté : {ext}")
