import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

LI_AT = "AQEDAVs2AxYDC03PAAABlyVnENEAAAGXSXOU0U0ATqlSgBjVeF1LL_gHhR2d0byOi2e-UMH1-hC0phnJTFHTUQsfvzvegmEh4dKm6bJrZ9BEY6kNWCrQzBfxH7i1oon14GJLgJy1ouCN9kzhcoUMlzLX"


# """
# playwright_scraper.py – Module pour extraire une offre d’emploi depuis différents sites.
# - extract_linkedin_job(url) : 
#     • Utilise Playwright headless pour naviguer sur LinkedIn.
#     • Attends le contenu, récupère titre, entreprise, lieu, description via CSS selectors.
# - extract_wttj_job(url) :
#     • Utilise Playwright pour naviguer sur WelcomeToTheJungle.
#     • Clique sur “Voir plus” (jusqu’à 3 fois) pour déplier la description.
#     • Recherche dans le DOM un <script type="application/ld+json"> contenant @type="JobPosting".
#     • Si trouvé, parse JSON-LD ; sinon, fallback sur balises <h1>, <a data-testid="company-link">, etc.
# - extract_job_posting(url) : 
#     • Détecte le domaine (LinkedIn vs WTTJ vs autres).
#     • Appelle la fonction correspondante ou renvoie {"error": "Site non supporté"}.
# """

async def extract_linkedin_job(page, url):
    """
    (Si besoin plus tard) extraction simplifiée sur LinkedIn.
    Pour l’instant, on se concentre sur WTTJ.
    """
    await page.goto(url, timeout=60000, wait_until="load")
    await page.wait_for_timeout(3000)
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(1000)

    async def first_visible_text(*selectors):
        for sel in selectors:
            locator = page.locator(sel)
            if await locator.count() > 0:
                try:
                    await locator.first.wait_for(state="visible", timeout=5000)
                    return await locator.first.text_content()
                except:
                    continue
        return ""

    title = await first_visible_text("h1.text-heading-xlarge", "h1")
    company = await first_visible_text("span.text-heading-small", "a.topcard__org-name-link")
    location = await first_visible_text("span.jobs-unified-top-card__bullet", "span.jobs-unified-top-card__location")
    description = await first_visible_text("div.jobs-description__container", "div.jobs-box__html-content")

    return {
        "title": title.strip() if title else "(Titre non trouvé)",
        "company": company.strip() if company else "(Entreprise non trouvée)",
        "location": location.strip() if location else "(Localisation non trouvée)",
        "description": description.strip() if description else "(Description non trouvée)"
    }


async def extract_wttj_job(page, url):
    # """
    # Extraction optimisée pour Welcome To The Jungle :
    # - On récupère d’abord le JSON-LD (JobPosting), qui contient
    #   Titre, Entreprise, Localisation + Description HTML complète.
    # - Si JSON-LD est absent ou incomplete, on retombe sur un fallback
    #   via BeautifulSoup pour capturer tout le <article> ou le <main>.
    # """

    # """
    # Extrait les données d’une fiche WelcomeToTheJungle :
    # - Navigue, attend l’élément main ou article.
    # - Clique sur “Voir plus” (jusqu’à 3 fois) pour dérouler la description entière.
    # - Récupère le <script type="application/ld+json"> contenant @type="JobPosting".
    # - Parse JSON-LD pour title, hiringOrganization.name, jobLocation.address.addressLocality, description.
    # - Si JSON-LD manquant, fallback sur balises <h1>, <a data-testid="company-link">, etc.
    # - Nettoyage de la description (supprimer balises HTML superflues).
    # - Retourne un dict { "title", "company", "location", "description" }.
    # """
    await page.goto(url, timeout=60000, wait_until="load")
    await page.wait_for_timeout(3000)

    # 1) Cliquer sur « Voir plus » (déplier éventuels blocs cachés)
    for _ in range(3):
        try:
            btn = page.locator("button:has-text('Voir plus')")
            if await btn.count() == 0:
                break
            await btn.first.click()
            await page.wait_for_timeout(1000)
        except:
            break

    # 2) Récupérer le contenu HTML après les déplieurs
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    # 3) Chercher le JSON-LD JobPosting
    title = company = location = None
    description_text = None

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except:
            continue

        # Si c'est un tableau, on cherche l'élément @type == "JobPosting"
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("@type") == "JobPosting":
                    data = item
                    break

        if isinstance(data, dict) and data.get("@type") == "JobPosting":
            # Titre
            if data.get("title"):
                title = data["title"].strip()
            # Entreprise
            if isinstance(data.get("hiringOrganization"), dict):
                company = data["hiringOrganization"].get("name", "").strip()
            # Localisation
            loc = data.get("jobLocation")
            if isinstance(loc, list) and loc:
                location = loc[0].get("address", {}).get("addressLocality", "").strip()
            elif isinstance(loc, dict):
                location = loc.get("address", {}).get("addressLocality", "").strip()

            # Description complète : le champ "description" dans JSON-LD est souvent en HTML
            if data.get("description"):
                # On passe par BeautifulSoup pour nettoyer les balises HTML
                description_html = data["description"]
                description_text = BeautifulSoup(description_html, "html.parser").get_text(separator="\n", strip=True)
            break

    # 4) Si certains champs manquent, fallback sur le DOM « visuel »
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
    if not company:
        # WTTJ a souvent un lien d’entreprise
        org = soup.select_one("a[data-testid='company-link']")
        if org:
            company = org.get_text(strip=True)
    if not location:
        # Souvent dans une balise span près du titre
        span_loc = soup.find("span", string=lambda t: t and "lieu" in t.lower())
        if span_loc:
            location = span_loc.get_text(strip=True)

    # 5) Si la description du JSON-LD n’existe pas ou est vide, on fait un fallback
    if not description_text:
        # Essayer de récupérer tout le contenu de l'<article> principal
        article = soup.find("article")
        if article:
            description_text = article.get_text(separator="\n", strip=True)

    if not description_text:
        # Sinon, prendre tout le <main>
        main = soup.find("main")
        if main:
            description_text = main.get_text(separator="\n", strip=True)

    if not description_text:
        # En dernier recours : tout le <body>
        body = soup.find("body")
        if body:
            description_text = body.get_text(separator="\n", strip=True)

    # Nettoyage final : si la description contient trop de nav/footer
    # On peut découper jusqu'à ce qu’on trouve l’intitulé du poste ou un mot-clé
    if description_text and title:
        lines = description_text.splitlines()
        cleaned = []
        for line in lines:
            # Si le titre apparaît, on garde tout à partir de là
            if title.lower() in line.lower():
                cleaned = lines[lines.index(line):]
                break
        if cleaned:
            description_text = "\n".join(cleaned).strip()

    # Si vraiment on n’a rien trouvé, on renvoie un message par défaut
    if not description_text:
        description_text = "(Description non trouvée)"

    return {
        "title": title or "(Titre non trouvé)",
        "company": company or "(Entreprise non trouvée)",
        "location": location or "(Localisation non trouvée)",
        "description": description_text
    }



async def extract_job_posting(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            )
        )

        # Si c’est un lien LinkedIn, on peut injecter un cookie li_at
        if "linkedin.com" in url:
            await context.add_cookies([{
                "name": "li_at",
                "value": LI_AT,
                "domain": ".linkedin.com",
                "path": "/",
                "secure": True,
                "httpOnly": True,
                "sameSite": "Lax"
            }])

        page = await context.new_page()

        if "linkedin.com" in url:
            job = await extract_linkedin_job(page, url)
        elif "welcometothejungle.com" in url:
            job = await extract_wttj_job(page, url)
        else:
            job = {"error": "Site non supporté."}

        await browser.close()
        return job
