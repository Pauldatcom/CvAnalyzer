# """
# job_runner.py – Script CLI pour lancer l’extraction d’une fiche de poste.
# - Appelé depuis Streamlit (via subprocess) avec l’URL de l’offre.
# - Utilise asyncio + Playwright (module playwright_scraper.extract_job_posting).
# - Retourne en stdout un JSON contenant { "title", "company", "location", "description" }.
# """

import sys
print("FICHIER EN COURS : job_runner.py", file=sys.stderr)
import asyncio
import json
from playwright_scraper import extract_job_posting

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        print(json.dumps({"error": "URL manquante"}))
        sys.exit(1)

    try:
        # ❌ on supprime totalement ce print :
        # print(f"[INFO] Ouverture de la page : {url}", file=sys.stderr)

        job = asyncio.run(extract_job_posting(url))
        print(json.dumps(job, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
