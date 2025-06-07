# scraper.py
from playwright.sync_api import sync_playwright
import time

def get_latest_results(limit=10):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.kwgin7.com/#/login")

            # Login
            page.fill('input[placeholder="Enter Username"]', "3089134")
            page.fill('input[placeholder="Enter Password"]', "freefire123")
            page.click("button:has-text('Login')")
            page.wait_for_timeout(3000)

            # Navigate to game record
            page.goto("https://www.kwgin7.com/#/gameRecord")
            page.wait_for_timeout(3000)

            periods = page.locator(".van-row .van-col span.text-center")
            numbers = page.locator(".van-row .lottery-history span:nth-child(2)")

            full_periods = [periods.nth(i).text_content().strip() for i in range(limit)]
            number_values = [int(numbers.nth(i).text_content().strip()) for i in range(limit)]

            results = []
            for i in range(len(full_periods)):
                num = number_values[i]
                color = "🟥 Red" if num in [3, 6, 9] else "🟩 Green" if num in [1, 4, 7] else "🟪 Violet"
                size = "Big" if num >= 5 else "Small"
                results.append({
                    "period": full_periods[i],
                    "number": num,
                    "color": color,
                    "size": size
                })

            browser.close()
            return results

    except Exception as e:
        print(f"Scraper error: {e}")
        return []
