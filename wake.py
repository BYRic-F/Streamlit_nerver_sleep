import re
import time
import random
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SITES = [
    "https://byric-f-project-reco-movie-streamlit-app-3pm0kb.streamlit.app/",
    "https://inseeprospectorcloud.streamlit.app/",
    "https://portfolio-f-bayen.streamlit.app/",
]

# On simplifie les mots-clés pour être plus efficace
KEYWORDS = ["Yes, get this app back up!", "Wake up"]

def run_wake():
    now_utc = datetime.now(timezone.utc)
    print(f"--- Execution: {now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC ---")

    # Anti-bot : Attente aléatoire entre 1 et 30 secondes avant de commencer
    wait_start = random.randint(1, 30)
    print(f"Waiting {wait_start}s to simulate human behavior...")
    time.sleep(wait_start)

    with sync_playwright() as p:
        # Launch avec des arguments pour éviter la détection
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        for url in SITES:
            print(f"Checking: {url}")
            try:
                # On charge la page
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Petit temps pour laisser le bouton apparaître si besoin
                page.wait_for_timeout(5000)

                clicked = False
                # Tentative de clic sur le bouton spécifique
                for kw in KEYWORDS:
                    # On cherche dans le document principal et les iframes
                    btn = page.get_by_role("button", name=re.compile(kw, re.I)).first
                    if btn.is_visible():
                        btn.click()
                        print(f"  [WAKE] Clicked '{kw}'")
                        clicked = True
                        break
                
                if not clicked:
                    # Si aucun bouton de réveil, on vérifie si l'app est déjà chargée
                    # (On cherche un élément typique de Streamlit comme la barre de menu)
                    if page.locator('button[kind="headerNoPadding"]').is_visible() or page.locator('.stApp').is_visible():
                        print("  [OK] App is already awake.")
                    else:
                        print("  [?] No wake button found, but app state unknown.")

                # On attend un peu pour valider le réveil avant de passer à la suivante
                page.wait_for_timeout(3000)

            except PlaywrightTimeoutError:
                print(f"  [TIMEOUT] {url} is taking too long.")
            except Exception as e:
                print(f"  [ERROR] {e}")

        browser.close()
    print("--- Finished ---\n")

if __name__ == "__main__":
    run_wake()