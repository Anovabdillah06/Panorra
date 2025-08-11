import re
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_logout_success(page: Page):
    page.goto("https://panorra.com/", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    expect(page).to_have_title(re.compile("Panorra"), timeout=60000)

    # Klik tombol Log In
    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=60000)
    login_link.click()

    # Isi email & password
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    expect(email_field).to_be_visible(timeout=60000)
    expect(password_field).to_be_visible(timeout=60000)
    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")

    # Klik tombol Log In
    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_enabled(timeout=60000)
    login_button.click()

    # Buka menu header
    menu_button = page.get_by_role("button", name="header menu")
    expect(menu_button).to_be_visible(timeout=60000)
    menu_button.click()

    # Klik tombol Log Out
    logout_link = page.get_by_role("link", name=" Log Out")
    expect(logout_link).to_be_visible(timeout=60000)
    logout_link.click()

    # Pastikan halaman kembali ke rekomendasi
    heading = page.get_by_role("heading", name="Recommendation for You")
    expect(heading).to_be_visible(timeout=60000)
