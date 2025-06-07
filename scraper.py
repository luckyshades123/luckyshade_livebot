
     # scraper.py

from playwright.sync_api import sync_playwright
import time

def get_latest_result():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.kwgin7.com/#/login")

            # Login
            page.fill('input[placeholder="Enter Username"]', "3089134")
            page.fill('input[placeholder="Enter Password"]', "freefire123")
            page.click("button:has-text('Login')")
            page.wait_for_timeout(3000)  # Wait for login to complete

            # Navigate to result page
            page.goto("https://www.kwgin7.com/#/gameRecord")
            page.wait_for_timeout(3000)

            # Extract latest result (this selector may need tweaking)
            full_period = page.locator(".period-number-selector").first.text_content().strip()
            number_text = page.locator(".result-number-selector").first.text_content().strip()

            number = int(number_text)
            color = "🟥 Red" if number in [3, 6, 9] else "🟩 Green" if number in [1, 4, 7] else "🟪 Violet"
            size = "Big" if number >= 5 else "Small"

            browser.close()
            return full_period, (number, color, size)

    except Exception as e:
        print(f"Error in scraper: {e}")
        return None, None   
