# scraper.py

from playwright.sync_api import sync_playwright
import time, os

def get_latest_result():
    try:
        username = "3089134"
        password = "freefire123"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.kwgin7.com/#/login")

            # Login flow
            page.fill('input[placeholder="Enter Username"]', username)
            page.fill('input[placeholder="Enter Password"]', password)
            page.click("button:has-text('Login')")
            page.wait_for_timeout(3000)

            # Navigate to game record page
            page.goto("https://www.kwgin7.com/#/gameRecord")
            page.wait_for_timeout(3000)

            # Try to extract the latest period and result number
            try:
                full_period = page.locator(".el-table__row .number").first.text_content().strip()
                number_text = page.locator(".el-table__row .open-code span").first.text_content().strip()
            except:
                print("⚠️ Selector structure changed or no data available.")
                browser.close()
                return None, None

            number = int(number_text)

            # Determine color and size
            color = (
                "🟥 Red" if number in [3, 6, 9]
                else "🟩 Green" if number in [1, 4, 7]
                else "🟪 Violet"
            )
            size = "Big" if number >= 5 else "Small"

            browser.close()
            return full_period, (number, color, size)

    except Exception as e:
        print(f"[SCRAPER ERROR] {e}")
        return None, None
