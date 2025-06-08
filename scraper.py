# scraper.py

import os
from playwright.async_api import async_playwright

async def get_latest_result(mode="1Min"):
    try:
        username = "3089134"
        password = "freefire123"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Go to login
            await page.goto("https://www.kwgin7.com/#/login")
            await page.fill('input[placeholder="Enter Username"]', username)
            await page.fill('input[placeholder="Enter Password"]', password)
            await page.click("button:has-text('Login')")
            await page.wait_for_timeout(3000)

            # Navigate to result page based on mode
            if mode == "3Min":
                await page.goto("https://www.kwgin7.com/#/gameRecord?type=3")
            else:  # Default is 1Min
                await page.goto("https://www.kwgin7.com/#/gameRecord")
            await page.wait_for_timeout(3000)

            # Extract latest period and number
            full_period = await page.locator(".el-table__row .number").first.text_content()
            number_text = await page.locator(".el-table__row .open-code span").first.text_content()

            number = int(number_text.strip())
            color = "🟥 Red" if number in [3, 6, 9] else "🟩 Green" if number in [1, 4, 7] else "🟪 Violet"
            size = "Big" if number >= 5 else "Small"

            await browser.close()
            return full_period.strip(), (number, color, size)

    except Exception as e:
        print(f"[SCRAPER ERROR] {e}")
        return None, None
