scraper.py

from playwright.sync_api import sync_playwright import time

def get_latest_result(): try: with sync_playwright() as p: browser = p.chromium.launch(headless=True) page = browser.new_page() page.goto("https://www.kwgin7.com/#/login")

# Login with credentials
        page.fill("input[placeholder='Please enter account']", "3089134")
        page.fill("input[placeholder='Please enter password']", "freefire123")
        page.click("button:has-text('Login')")

        page.wait_for_timeout(3000)
        page.goto("https://www.kwgin7.com/#/lottery")
        page.wait_for_timeout(4000)

        # Read latest result (example structure — adjust if needed)
        period = page.query_selector(".game_num span").inner_text()
        last_number_el = page.query_selector(".open-num span:last-child")
        number = int(last_number_el.inner_text()) if last_number_el else None

        # Determine color
        if number in [0, 5]:
            color = "🟪 Violet"
        elif number in [1, 3, 7, 9]:
            color = "🟩 Green"
        elif number in [2, 4, 6, 8]:
            color = "🟥 Red"
        else:
            color = "Unknown"

        size = "Big" if number >= 5 else "Small"
        browser.close()

        return period, (number, color, size)

except Exception as e:
    print(f"[Scraper Error] {e}")
    return None, None

