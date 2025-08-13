# test_logout.py
import re
import pytest
from playwright.sync_api import Page

@pytest.mark.smoke
def test_logout_success(page: Page):
    # Login terlebih dahulu
    page.goto("https://panorra.com/", timeout=60000)
    assert "Panorra" in page.title()

    page.get_by_role("link", name="Log In").click()
    page.get_by_placeholder("Enter your email or username").fill("arnov@grr.la")
    page.get_by_placeholder("Enter your password").fill("Ar_061204")
    page.get_by_role("button", name="Log In").click()

    heading = page.get_by_role("heading", name="Recommendation for You")
    assert heading.is_visible()

    # Klik menu profile/logout
    profile_menu = page.get_by_role("button", name="Profile")
    assert profile_menu.is_visible()
    profile_menu.click()

    logout_button = page.get_by_role("button", name="Log Out")
    assert logout_button.is_visible()
    logout_button.click()

    # Validasi berhasil logout
    assert page.get_by_role("link", name="Log In").is_visible()


@pytest.mark.regression
def test_not_logged_out(page: Page):
    page.goto("https://panorra.com/", timeout=60000)
    page.get_by_role("link", name="Log In").click()
    page.get_by_placeholder("Enter your email or username").fill("arnov@grr.la")
    page.get_by_placeholder("Enter your password").fill("Ar_061204")
    page.get_by_role("button", name="Log In").click()

    page.get_by_role("button", name="Profile").click()

    # Cek URL
    assert re.match(r"https://panorra\.com/?", page.url)


@pytest.mark.unit
def test_logout_button_visibility(page: Page):
    page.goto("https://panorra.com/", timeout=60000)
    page.get_by_role("link", name="Log In").click()
    page.get_by_placeholder("Enter your email or username").fill("arnov@grr.la")
    page.get_by_placeholder("Enter your password").fill("Ar_061204")
    page.get_by_role("button", name="Log In").click()

    # Pastikan tombol logout muncul
    page.get_by_role("button", name="Profile").click()
    logout_button = page.get_by_role("button", name="Log Out")
    assert logout_button.is_visible()
