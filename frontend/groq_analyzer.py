# groq_analyzer.py

# """
# groq_analyzer.py – Module d’interaction avec l’API Groq (LLaMA 3) pour :
# - Analyser l’écart entre le CV et la fiche de poste.
# - Générer un CV réécrit à partir des suggestions.
# - Obtenir un score de compatibilité (0–100).
# """

# GROQ_API_URL doit être mis à jour si vous avez une URL différente.
# API_KEY lu depuis .env, on lève ValueError si absent.
# Chaque fonction construit un “system_prompt” (mission) et “user_prompt” (le contexte).
# On utilise requests.post() et resp.raise_for_status() pour gérer les erreurs HTTP.
# Dans score_cv(), on nettoie la réponse brute pour extraire uniquement l’entier.


import os
import requests

def analyze_cv_and_offer(cv_text: str, offer_text: str) -> str:
    """
    Envoie au modèle LLaMA 3 le CV et la fiche de poste,
    et retourne un texte structuré : écarts, suggestions, questions, roadmap.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("La clé GROQ_API_KEY est manquante dans l'environnement.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "Tu es un expert en recrutement et en ressources humaines. "
        "On va te fournir deux blocs de texte :\n"
        "  1. Le contenu complet d'un CV (texte brut).\n"
        "  2. Le contenu complet d'une fiche de poste (texte brut).\n\n"
        "Ta mission :\n"
        "- Analyser les écarts entre le CV et la fiche de poste.\n"
        "- Pour chaque écart, proposer des suggestions très concrètes : compétences à ajouter, expériences à mentionner, etc.\n"
        "- Proposer des questions d'entretien probables en lien avec la fiche de poste.\n"
        "- Donner une roadmap détaillée pour acquérir les compétences manquantes.\n"
        "- En fin de réponse, rends **uniquement** le texte des suggestions structurées (ne répète pas le CV ni la fiche de poste).\n"
    )

    user_prompt = (
        f"=== CV ORIGINAL ===\n{cv_text}\n\n"
        f"=== FICHE DE POSTE ===\n{offer_text}\n\n"
        "=== RÉALISE TON ANALYSE CI-DESSOUS : ==="
    )

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"]


def generate_updated_cv(cv_text: str, suggestions: str) -> str:
    """
    Réécrit le CV en insérant directement les suggestions (réalisé par LLaMA 3).
    Retourne le texte complet du CV mis à jour.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("La clé GROQ_API_KEY est manquante dans l'environnement.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = (
    "Tu es un expert en recrutement RH. On va te fournir :\n"
    "  1. Un CV complet (texte brut).\n"
    "  2. Une liste de suggestions pour l'améliorer.\n\n"
    "Ta mission :\n"
    "- Réécrire le CV en intégrant les améliorations **sans répéter ce qui est déjà présent**.\n"
    "- Si des expériences sont manquantes mais peuvent être simulées sous forme de projets personnels ou formations pertinentes, ajoute-les (sans mentir).\n"
    "- Adapter le **style rédactionnel** à celui de la fiche de poste :\n"
    "    • sobre, professionnel et structuré pour les grandes entreprises (ex: CGI),\n"
    "    • plus dynamique et synthétique pour des start-ups.\n"
    "- Respecter la structure du CV d’origine : titres, listes, puces, majuscules, etc.\n"
    "- Améliorer la lisibilité, la formulation, et éviter les redondances ou listes trop longues.\n"
    "- À la fin, retourne uniquement le texte final du CV, prêt à être converti en PDF."
    )   


    user_prompt = (
        f"=== CV ORIGINAL ===\n{cv_text}\n\n"
        f"=== SUGGESTIONS IA ===\n{suggestions}\n\n"
        "=== RÉÉCRIS LE CV MIS À JOUR ICI : ==="
    )

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"]


def score_cv(cv_text: str, offer_text: str) -> int:
    """
    Demande au modèle LLaMA 3 de donner un score (entier de 0 à 100) 
    indiquant le degré de correspondance du CV à la fiche de poste.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("La clé GROQ_API_KEY est manquante dans l'environnement.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "Tu es un ancien recruteur, maintenant expert IA. "
        "Tu vas évaluer à quel point un CV correspond à une fiche de poste.\n"
        "- Renvoie **uniquement** un entier de 0 à 100 (0 = aucune correspondance, 100 = match parfait).\n"
        "- Ne fais pas de commentaire, ne renvoie pas de texte explicatif.\n"
    )

    user_prompt = (
        f"=== CV ORIGINAL ===\n{cv_text}\n\n"
        f"=== FICHE DE POSTE ===\n{offer_text}\n\n"
        "=== DONNE LE SCORE (0 à 100) : ==="
    )

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        "temperature": 0.0
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    reply = result["choices"][0]["message"]["content"].strip()

    # On tente de récupérer un entier dans la réponse
    try:
        score = int("".join(ch for ch in reply if ch.isdigit()))
    except:
        score = 0
    return score
