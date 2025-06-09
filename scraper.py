# scraper.py

import os
from playwright.async_api import async_playwright

async def get_latest_result(mode="1Min"):
    """
    Fetch the latest period and result (number, color, size) from KWG.
    """
    try:
        username = "3089134"
        password = "freefire123"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Login
            await page.goto("https://www.kwgin7.com/#/login")
            await page.fill('input[placeholder="Enter Username"]', username)
            await page.fill('input[placeholder="Enter Password"]', password)
            await page.click("button:has-text('Login')")
            await page.wait_for_timeout(3000)

            # Navigate to correct game record
            if mode == "3Min":
                await page.goto("https://www.kwgin7.com/#/gameRecord?type=3")
            else:
                await page.goto("https://www.kwgin7.com/#/gameRecord")

            await page.wait_for_timeout(3000)

            # Extract latest
            full_period = await page.locator(".el-table__row .number").first.text_content()
            number_text = await page.locator(".el-table__row .open-code span").first.text_content()
            number = int(number_text.strip())

            color = "🟥 Red" if number in [3, 6, 9] else "🟩 Green" if number in [1, 4, 7] else "🟪 Violet"
            size = "Big" if number >= 5 else "Small"

            await browser.close()
            return full_period.strip(), (number, color, size)

    except Exception as e:
        print(f"[SCRAPER ERROR - get_latest_result] {e}")
        return None, None


async def get_latest_results(limit=20, mode="1Min"):
    """
    Return a list of last `limit` results for prediction analysis.
    Format: [{'number': x, 'color': y, 'size': z}, ...]
    """
    try:
        username = "3089134"
        password = "freefire123"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Login
            await page.goto("https://www.kwgin7.com/#/login")
            await page.fill('input[placeholder="Enter Username"]', username)
            await page.fill('input[placeholder="Enter Password"]', password)
            await page.click("button:has-text('Login')")
            await page.wait_for_timeout(3000)

            # Navigate to result page
            if mode == "3Min":
                await page.goto("https://www.kwgin7.com/#/gameRecord?type=3")
            else:
                await page.goto("https://www.kwgin7.com/#/gameRecord")

            await page.wait_for_timeout(3000)

            results = []
            rows = page.locator(".el-table__row")
            count = await rows.count()

            for i in range(min(count, limit)):
                try:
                    number_text = await rows.nth(i).locator(".open-code span").first.text_content()
                    number = int(number_text.strip())
                    color = "🟥 Red" if number in [3, 6, 9] else "🟩 Green" if number in [1, 4, 7] else "🟪 Violet"
                    size = "Big" if number >= 5 else "Small"
                    results.append({"number": number, "color": color, "size": size})
                except Exception as e:
                    print(f"[SCRAPER] Failed to parse row {i}: {e}")
                    continue

            await browser.close()
            return results

    except Exception as e:
        print(f"[SCRAPER ERROR - get_latest_results] {e}")
        return []
