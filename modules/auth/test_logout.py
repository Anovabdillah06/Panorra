import re
import pytest
from playwright.sync_api import Page, expect

# Tes untuk memastikan proses logout berhasil
@pytest.mark.smoke
def test_logout_success(page: Page):
    # Buka halaman utama
    page.goto("https://panorra.com/", timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    # Klik tombol Log In
    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=10000)
    login_link.click()

    # Isi email & password
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    expect(email_field).to_be_visible(timeout=10000)
    expect(password_field).to_be_visible(timeout=10000)
    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")

    # Klik tombol Log In
    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_enabled(timeout=10000)
    login_button.click()

    # Tunggu heading "Recommendation for You" muncul
    heading = page.get_by_role("heading", name="Recommendation for You")
    expect(heading).to_be_visible(timeout=30000)

    # Buka menu header setelah login
    menu_button = page.get_by_role("button", name="header menu")
    expect(menu_button).to_be_visible(timeout=10000)
    menu_button.click()

    # Klik tombol Log Out
    logout_link = page.get_by_role("link", name=" Log Out")
    expect(logout_link).to_be_visible(timeout=10000)
    logout_link.click()

    # Assertion setelah logout
    heading_after_logout = page.get_by_role("heading", name="Recommendation for You")
    expect(heading_after_logout).to_be_visible(timeout=10000)
    
    login_link_after_logout = page.get_by_role("link", name="Log In")
    expect(login_link_after_logout).to_be_visible(timeout=10000)
    
    # Assert untuk memastikan kembali ke halaman awal
    assert page.url == "https://panorra.com/", "URL tidak kembali ke halaman utama setelah logout."

#-------------------------------------------------------------------------------------------------------------------

# Tes untuk memastikan pengguna tetap login
@pytest.mark.regression
def test_not_logged_out(page: Page):
    # Buka halaman utama
    page.goto("https://panorra.com/", timeout=30000)
    
    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=10000)
    login_link.click()
    
    email_field = page.get_by_role("textbox", name="Enter your email or username")
    password_field = page.get_by_role("textbox", name="Enter your password")
    expect(email_field).to_be_visible(timeout=10000)
    expect(password_field).to_be_visible(timeout=10000)
    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")

    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_enabled(timeout=10000)
    login_button.click()
    
    # Assertion: Cek elemen setelah login
    header_menu_button = page.get_by_role("button", name="header menu")
    expect(header_menu_button).to_be_visible(timeout=10000)
    
    recommendation_heading = page.get_by_role("heading", name="Recommendation for You")
    expect(recommendation_heading).to_be_visible(timeout=10000)
    
    page.screenshot(path="screenshots/regression/recommendation_page_passed.png")
    
#-------------------------------------------------------------------------------------------------------------------

# Tes unit untuk fungsionalitas logout
@pytest.mark.unit
def test_logout_unit(page: Page):
    # Buka halaman utama
    page.goto("https://panorra.com/", timeout=30000)
    
    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=10000)
    login_link.click()
    
    email_field = page.get_by_role("textbox", name="Enter your email or username")
    password_field = page.get_by_role("textbox", name="Enter your password")
    expect(email_field).to_be_visible(timeout=10000)
    expect(password_field).to_be_visible(timeout=10000)
    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")

    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_enabled(timeout=10000)
    login_button.click()
    
    # Menunggu heading terlihat setelah login berhasil
    header_menu_button = page.get_by_role("button", name="header menu")
    expect(header_menu_button).to_be_visible(timeout=10000)
    
    header_menu_button.click()

    logout_button = page.get_by_role("link", name=" Log Out")
    expect(logout_button).to_be_visible(timeout=10000)
    logout_button.click()
    
    # Menunggu heading terlihat setelah logout
    recommendation_heading = page.get_by_role("heading", name="Recommendation for You")
    expect(recommendation_heading).to_be_visible(timeout=10000)
    
    page.screenshot(path="screenshots/unit/logout_passed.png")