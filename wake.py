import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SITES = [
    "https://cinemadelacite.streamlit.app/",
    "https://byric-f-project-reco-movie-streamlit-app-3pm0kb.streamlit.app/",
    "https://inseeprospectorcloud.streamlit.app/",
    "https://portfolio-f-bayen.streamlit.app/",
    "https://appappentificator-nyglupew87ankibbekpltd.streamlit.app/",
]

# Mots-clés du bouton (priorité à la phrase exacte)
KEYWORDS = [
    "Yes, get this app back up!",
    "yes",
    "get it",
    "back up",
    "wake",
    "start",
]

now_utc = datetime.now(timezone.utc)
print(f"Wake Streamlit — {now_utc.isoformat()}")

now_fr = now_utc.astimezone(ZoneInfo("Europe/Paris"))
print(f"Heure FR : {now_fr.strftime('%Y-%m-%d %H:%M:%S')}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    # Utiliser un user agent plus standard pour éviter d'être bloqué
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    for url in SITES:
        print(f"\n Opening {url}")

        try:
            # Attendre que le shell initial soit chargé
            page.goto(url, wait_until="domcontentloaded", timeout=120_000)
            # Attendre un peu que le JS de Streamlit détermine si l'app dort
            page.wait_for_timeout(10000)

            clicked = False

            # On cherche le bouton dans la page ET dans les iframes
            for kw in KEYWORDS:
                pattern = re.compile(rf".*{re.escape(kw)}.*", re.IGNORECASE)
                
                # Liste des locators à tester : page principale et iframes
                locators = [
                    page.get_by_role("button", name=pattern),
                    page.frame_locator("iframe").get_by_role("button", name=pattern),
                    page.get_by_text(pattern), # Fallback si pas role='button'
                    page.frame_locator("iframe").get_by_text(pattern)
                ]

                for btn in locators:
                    if btn.count() > 0:
                        btn.first.click(timeout=30_000)
                        print(f"Clicked button/text matching keyword: '{kw}'")
                        clicked = True
                        break
                
                if clicked:
                    break

            if not clicked:
                # Si rien trouvé, on tente un dernier recours sur n'importe quel bouton visible
                any_btn = page.locator("button:visible").first
                if any_btn.count() > 0:
                    any_btn.click(timeout=15_000)
                    print("Clicked first visible <button> (fallback)")
                    clicked = True
                else:
                    print("Aucun bouton trouvé. L'application est peut-être déjà active.")

            # Laisser le temps à Streamlit de lancer le réveil
            page.wait_for_timeout(5000)
            print("Done")

        except PlaywrightTimeoutError:
            print("Timeout Playwright → application très lente ou bloquée")
        except Exception as e:
            print(f"Erreur → {e}")

    browser.close()
