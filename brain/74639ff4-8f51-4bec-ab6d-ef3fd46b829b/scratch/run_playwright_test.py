import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Listen to console logs
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
        # Listen to page errors
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))
        # Listen to failed requests
        page.on("requestfailed", lambda req: print(f"[REQ FAILED] {req.method} {req.url}: {req.failure}"))
        
        # Mock window.confirm to return True (accept confirm dialog)
        await page.add_init_script("window.confirm = () => true;")
        
        print("Navigating to http://localhost:5173/...")
        await page.goto("http://localhost:5173/")
        await page.wait_for_timeout(2000)
        
        # Click on INVENTORY in sidebar
        print("Navigating to Inventory...")
        inventory_link = page.locator("text=INVENTORY")
        if await inventory_link.count() > 0:
            await inventory_link.click()
            await page.wait_for_timeout(2000)
        
        # Find and click "CLEAR ALL ASSETS"
        print("Clicking CLEAR ALL ASSETS...")
        clear_btn = page.locator("text=CLEAR ALL ASSETS")
        if await clear_btn.count() > 0:
            await clear_btn.click()
            await page.wait_for_timeout(3000)
        else:
            print("CLEAR ALL ASSETS button not found on page.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
