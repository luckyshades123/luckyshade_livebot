from playwright.sync_api import sync_playwright
import time

def get_latest_result():
    try:
        username = "3089134"
        password = "freefire123"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Login
            page.goto("https://www.kwgin7.com/#/login")
            page.fill('input[placeholder="Enter Username"]', username)
            page.fill('input[placeholder="Enter Password"]', password)
            page.click("button:has-text('Login')")
            page.wait_for_timeout(3000)

            # Navigate to game record
            page.goto("https://www.kwgin7.com/#/gameRecord")
            page.wait_for_timeout(3000)

            # Extract latest result
            full_period = page.locator(".el-table__row .number").first.text_content().strip()
            number_text = page.locator(".el-table__row .open-code span").first.text_content().strip()
            number = int(number_text)

            color = "🟥 Red" if number in [3, 6, 9] else "🟩 Green" if number in [1, 4, 7] else "🟪 Violet"
            size = "Big" if number >= 5 else "Small"

            browser.close()
            return full_period, (number, color, size)

    except Exception as e:
        print(f"[SCRAPER ERROR - get_latest_result] {e}")
        return None, None


def get_latest_results(limit=10):
    try:
        username = "3089134"
        password = "freefire123"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Login
            page.goto("https://www.kwgin7.com/#/login")
            page.fill('input[placeholder=\"Enter Username\"]', username)
            page.fill('input[placeholder=\"Enter Password\"]', password)
            page.click("button:has-text('Login')")
            page.wait_for_timeout(3000)

            # Navigate to game record
            page.goto("https://www.kwgin7.com/#/gameRecord")
            page.wait_for_timeout(3000)

            results = []
            rows = page.locator(".el-table__row")
            count = min(rows.count(), limit)

            for i in range(count):
                try:
                    number_text = rows.nth(i).locator(".open-code span").first.text_content().strip()
                    number = int(number_text)

                    color = "🟥 Red" if number in [3, 6, 9] else "🟩 Green" if number in [1, 4, 7] else "🟪 Violet"
                    size = "Big" if number >= 5 else "Small"

                    results.append({
                        "number": number,
                        "color": color,
                        "size": size
                    })
                except Exception as e:
                    print(f"[SCRAPER] Failed to parse row {i}: {e}")
                    continue

            browser.close()
            return results

    except Exception as e:
        print(f"[SCRAPER ERROR - get_latest_results] {e}")
        return []
