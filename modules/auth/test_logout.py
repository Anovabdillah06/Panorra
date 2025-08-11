import re
import pytest
from playwright.async_api import Page

# Smoke Test
@pytest.mark.smoke
async def test_smoke_logout(page: Page):
    await page.goto("https://panorra.com/", timeout=60000)
    await page.wait_for_load_state("domcontentloaded")

    assert "Panorra" in await page.title()

    await page.get_by_role("link", name="Log In").click()
    await page.wait_for_load_state("networkidle")

    await page.get_by_placeholder("Enter your email or username").fill("arnov@grr.la")
    await page.get_by_placeholder("Enter your password").fill("Ar_061204")
    await page.get_by_role("button", name="Log In").click()

    await page.get_by_role("heading", name="Recommendation for You").wait_for(state="visible")

    await page.get_by_role("button", name="header menu").click()
    await page.get_by_role("link", name="Log Out").click()

    await page.get_by_role("link", name="Log In").wait_for(state="visible")
    assert await page.get_by_role("link", name="Log In").is_visible()


# Regression Test
@pytest.mark.regression
async def test_visible_logged_out(page: Page):
    await page.goto("https://panorra.com/", timeout=60000)
    await page.wait_for_load_state("domcontentloaded")

    assert "Panorra" in await page.title()

    await page.get_by_role("link", name="Log In").click()
    await page.wait_for_load_state("networkidle")

    await page.get_by_placeholder("Enter your email or username").fill("arnov@grr.la")
    await page.get_by_placeholder("Enter your password").fill("Ar_061204")
    await page.get_by_role("button", name="Log In").click()

    await page.get_by_role("heading", name="Recommendation for You").wait_for(state="visible")

    await page.get_by_role("button", name="header menu").click()
    await page.get_by_role("link", name="Log Out").click()

    login_link = page.get_by_role("link", name="Log In")
    await login_link.wait_for(state="visible")
    assert await login_link.is_visible()


# Unit Test
@pytest.mark.unit
async def test_unit_logout(page: Page):
    await page.goto("https://panorra.com/", timeout=60000)
    await page.wait_for_load_state("domcontentloaded")

    assert "Panorra" in await page.title()

    await page.get_by_role("link", name="Log In").click()
    await page.wait_for_load_state("networkidle")

    await page.get_by_placeholder("Enter your email or username").fill("arnov@grr.la")
    await page.get_by_placeholder("Enter your password").fill("Ar_061204")
    await page.get_by_role("button", name="Log In").click()

    await page.get_by_role("heading", name="Recommendation for You").wait_for(state="visible")

    await page.get_by_role("button", name="header menu").click()

    logout_link = page.get_by_role("link", name="Log Out")
    await logout_link.wait_for(state="visible")
    assert await logout_link.is_visible()

    await logout_link.click()
    await page.get_by_role("link", name="Log In").wait_for(state="visible")
    assert await page.get_by_role("link", name="Log In").is_visible()
