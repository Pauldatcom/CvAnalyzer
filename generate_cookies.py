# generate_cookies.py

import asyncio
from playwright.async_api import async_playwright
import json

OUTPUT_FILE = "linkedin_cookies.json"
LINKEDIN_URL = "https://www.linkedin.com/login"

async def save_linkedin_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Lancement en mode non-headless
        context = await browser.new_context()
        page = await context.new_page()

        print(f"[INFO] Ouverture de la page de connexion LinkedIn : {LINKEDIN_URL}")
        await page.goto(LINKEDIN_URL)

        print("[INFO] Connectez-vous manuellement à LinkedIn dans la fenêtre ouverte.")
        print("Appuyez sur ENTRÉE ici quand vous avez terminé...")

        input()  # Attente que l'utilisateur confirme après login

        cookies = await context.cookies()
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)

        print(f"[✅] Cookies LinkedIn enregistrés dans : {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(save_linkedin_cookies())
