# 🧠 CVAnalyzer – Assistant IA pour l’analyse de CV & simulation d’entretien

## 🎯 Objectif

CVAnalyzer est une application IA complète qui permet de :

- 📄 Analyser un CV en lien avec une offre d’emploi
- 🤖 Obtenir des suggestions d’amélioration
- 🧠 Générer des questions d’entretien ciblées
- 📈 Créer une roadmap de montée en compétences
- 🗣️ Simuler un entretien vocal en temps réel avec IA

---

## 🛠️ Technologies utilisées

| Composant       | Technologie                 |
| --------------- | --------------------------- |
| Frontend        | Streamlit                   |
| Backend         | FastAPI                     |
| Scraping        | Playwright (WTTJ)           |
| Analyse IA      | LLaMA 3 via Groq            |
| Entretien vocal | LiveKit + Whisper + Mistral |
| PDF Export      | FPDF                        |
| Hébergement     | Railway                     |

---

## 🚀 Fonctionnalités principales

### 📊 Analyse IA du CV

- Upload d’un CV (.pdf ou .txt)
- Extraction automatique d’une offre (via lien Welcome to the Jungle)
- Appel à LLaMA 3 pour générer :
  - Une analyse comparative CV / offre
  - Des suggestions d’amélioration
  - Des questions probables d’entretien
  - Une roadmap personnalisée

### ✏️ Génération d’un CV amélioré

- Réécriture du CV selon les recommandations IA

### Assitant textuel, chatbot textuel

- Intéraction textuel avec un historique, question d'entretien.

### 🗣️ Assistant vocal RH

- Simulation d’un entretien vocal
- Interaction audio/audio avec l’utilisateur
- Analyse en temps réel via Whisper et Mistral

---

## 🧪 Démo en ligne

👉 [Lien vers l'application Streamlit](https://cvanalyzerforyou.streamlit.app/Analyse_IA_du_profil)  
👉 [Backend Railway](https://cvanalyzer-production-1322.up.railway.app)

---

## 🔧 Lancer en local

### Prérequis :

- Python 3.10+
- Node.js (pour Playwright)
- `playwright install`

### Installation :

```bash
cd backend
pip install -r requirements.txt
playwright install --with-deps
uvicorn server:app --reload
```

```bash
cd frontend
streamlit run app.py
```

---

## 🙋‍♂️ Auteurs

- [Paul Compagnon]
- Projet d'équipe / académique — 2025
