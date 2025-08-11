import pytest
from playwright.async_api import async_playwright

# =============================
# SMOKE TEST
# =============================
@pytest.mark.smoke
@pytest.mark.asyncio
async def test_logout_smoke():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Login
        await page.goto("https://panorra.com/", timeout=20000)
        await page.get_by_role("link", name="Log In").click()
        await page.fill('input[placeholder="Enter your email or username"]', "arnov@grr.la")
        await page.fill('input[placeholder="Enter your password"]', "Ar_061204")
        await page.get_by_role("button", name="Log In").click()
        await page.wait_for_timeout(2000)

        # Logout
        await page.get_by_role("button", name="header menu").click()
        await page.get_by_role("link", name=" Log Out").click()
        await page.wait_for_timeout(2000)

        # Assertion: pastikan tombol "Log In" muncul lagi
        assert await page.is_visible('text="Log In"'), "Logout gagal - tombol 'Log In' tidak ditemukan"

        await browser.close()

# =============================
# REGRESSION TEST
# =============================
@pytest.mark.regression
@pytest.mark.asyncio
async def test_visible_logged_out():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Contoh alur logout
        await page.goto("https://example.com/dashboard")
        await page.click("#logoutButton")
        
        # Assertion
        assert await page.is_visible("#loginPage") is True
        
        await browser.close()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_logout_unit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Langsung ke halaman login untuk unit test UI
        await page.goto("https://example.com/login")
        
        # Assertion elemen setelah logout
        assert await page.is_visible("#usernameInput")
        assert await page.is_visible("#passwordInput")
        
        await browser.close()