import re
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.smoke
def test_login_success(page: Page):
    page.goto("https://panorra.com/", timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    expect(page).to_have_title(re.compile("Panorra"), timeout=15000)

    # Menunggu link login terlihat, lalu klik
    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=10000)
    login_link.click()

    # Menunggu input field muncul sebelum diisi
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    expect(email_field).to_be_visible(timeout=10000)
    expect(password_field).to_be_visible(timeout=10000)
    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")

    # Tombol login otomatis menjadi enabled setelah diisi, cukup tunggu sampai enabled
    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_enabled(timeout=10000)
    login_button.click()
    
    # Menunggu heading terlihat setelah login berhasil
    heading = page.get_by_role("heading", name="Recommendation for You")
    expect(heading).to_be_visible(timeout=10000)

    assert heading.inner_text().strip() == "Recommendation for You", "Teks heading tidak sesuai"


# --- Bagian test_login_invalid_credentials ---
@pytest.mark.regression
def test_login_invalid_credentials(page: Page):
    page.goto("https://panorra.com/", timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    expect(page).to_have_title(re.compile("Panorra"), timeout=10000)

    # Menunggu dan klik link login
    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=10000)
    login_link.click()
    
    # Menunggu input field muncul
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    expect(email_field).to_be_visible(timeout=10000)
    expect(password_field).to_be_visible(timeout=10000)
    
    email_field.fill("timbel@gmail.com")
    password_field.fill("Ar_061204")
    
    # Tunggu tombol login tersedia dan klik
    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_enabled(timeout=10000)
    login_button.click()
    
    # Menunggu pesan error muncul
    error_message = page.locator("text=Email or Password incorrect")
    expect(error_message).to_be_visible(timeout=10000)

    assert error_message.inner_text().strip() == "Email or Password incorrect", "Pesan error tidak sesuai"


# --- Bagian test_login_button_disabled_when_empty ---
@pytest.mark.regression
def test_login_button_disabled_when_empty(page: Page):
    page.goto("https://panorra.com/", timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    expect(page).to_have_title(re.compile("Panorra"), timeout=10000)

    # Klik link login
    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=10000)
    login_link.click()
    
    # Menunggu tombol login muncul, lalu cek apakah disabled
    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_disabled(timeout=10000)
    
    assert not login_button.is_enabled(), "Tombol login seharusnya disabled ketika field kosong"


# --- Bagian test_login_page_ui_elements ---
@pytest.mark.unit
def test_login_page_ui_elements(page: Page):
    page.goto("https://panorra.com/", timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=10000)
    login_link.click()
    
    # Tunggu elemen-elemen UI terlihat
    expect(page.get_by_placeholder("Enter your email or username")).to_be_visible(timeout=10000)
    expect(page.get_by_placeholder("Enter your password")).to_be_visible(timeout=10000)
    expect(page.get_by_text("Password", exact=True)).to_be_visible(timeout=10000)
    expect(page.get_by_text("Email/Username", exact=True)).to_be_visible(timeout=10000)
    expect(page.get_by_role("heading", name="Log In to Panorra")).to_be_visible(timeout=10000)
    expect(page.get_by_text("Forgot your password?")).to_be_visible(timeout=10000)
    expect(page.get_by_text("OR", exact=True)).to_be_visible(timeout=10000)
    expect(page.get_by_text("Need a Panorra account?")).to_be_visible(timeout=10000)

    # Perbaikan: gunakan page.locator() untuk mendapatkan locator dari iframe, 
    # lalu gunakan expect() untuk memeriksa visibilitasnya.
    iframe_locator = page.locator('iframe[title*="Google"]')
    expect(iframe_locator).to_be_visible(timeout=10000)

    # Kode ini tetap benar, karena Anda menggunakan frame_locator untuk menemukan button di dalam iframe
    google_iframe = page.frame_locator('iframe[title*="Google"]')
    expect(google_iframe.get_by_role("button")).to_be_visible(timeout=10000)
    
    # Assertion tambahan
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    assert email_field.get_attribute("placeholder") == "Enter your email or username", "Placeholder email tidak sesuai"
    assert password_field.get_attribute("placeholder") == "Enter your password", "Placeholder password tidak sesuai"