import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SITES = [
    "https://cinemadelacite.streamlit.app/",
    "https://byric-f-project-reco-movie-streamlit-app-3pm0kb.streamlit.app/",
    "https://inseeprospectorcloud.streamlit.app/",
]

# Mots-clés du bouton
KEYWORDS = [
    "yes",
    "get it",
    "back up",
    "wake",
    "start",
    "run",
    "launch",
    "go",
]

now_utc = datetime.now(timezone.utc)
print(f"Wake Streamlit — {now_utc.isoformat()}")

now_fr = now_utc.astimezone(ZoneInfo("Europe/Paris"))
print(f"Heure FR : {now_fr.strftime('%Y-%m-%d %H:%M:%S')}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for url in SITES:
        print(f"\n Opening {url}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=180_000)

            page.wait_for_timeout(8000)

            clicked = False

            # Trouver un bouton dont le nom matche un mot-clé
            for kw in KEYWORDS:
                pattern = re.compile(rf".*{re.escape(kw)}.*", re.IGNORECASE)
                btn = page.get_by_role("button", name=pattern)

                if btn.count() > 0:
                    # clique le premier bouton correspondant
                    btn.first.click(timeout=30_000)
                    print(f"Clicked button matching keyword: '{kw}'")
                    clicked = True
                    break

            # Si rien trouvé, clique le premier bouton visible
            if not clicked:
                any_btn = page.locator("button:visible").first
                if any_btn.count() > 0:
                    any_btn.click(timeout=30_000)
                    print("Clicked first visible <button> (fallback)")
                    clicked = True
                else:
                    print("Aucun bouton visible trouvé (peut-être déjà awake ou UI différente).")

            # Laisser le temps à Streamlit de rerun après clic
            page.wait_for_timeout(6000)

            print("Done")

        except PlaywrightTimeoutError:
            print("Timeout Playwright → cold start très probable / app lente")
        except Exception as e:
            print(f"Erreur → {e}")

    browser.close()
