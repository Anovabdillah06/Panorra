import re
import pytest
from playwright.sync_api import Page, expect
from pathlib import Path

# -------------------------------
# Helper
# -------------------------------
def fill_input(page: Page, placeholder: str, value: str):
    field = page.get_by_placeholder(placeholder)
    field.fill("")  # clear dulu
    field.fill(value)
    # Catatan: Baris di bawah ini umumnya tidak diperlukan.
    # Playwright '.fill()' sudah sangat andal.
    # page.evaluate(f'document.querySelector("[placeholder=\'{placeholder}\']").value = "{value}"')
    return field

# -------------------------------
# Test login
# -------------------------------
@pytest.mark.smoke
def test_login_success(page: Page, base_url, username, password):
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    expect(page).to_have_title(re.compile("Panorra"), timeout=15000)

    page.get_by_role("link", name="Log In").click()
    fill_input(page, "Enter your email or username", username)
    fill_input(page, "Enter your password", password)

    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_enabled(timeout=10000)
    login_button.click()

    # --- JEDA PINTAR DITAMBAHKAN DI SINI ---
    # Menunggu hingga halaman selesai memuat dan aktivitas jaringan tenang.
    # Ini memberikan waktu bagi server untuk memproses login dan merender halaman berikutnya.
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception as e:
        print(f"Halaman tidak mencapai networkidle, mungkin karena ada aktivitas latar belakang. Melanjutkan tes... Error: {e}")


    # Setelah jeda, baru kita cari elemen di halaman baru.
    heading = page.get_by_role("heading", name="Recommendation for You")
    expect(heading).to_be_visible(timeout=10000)
    assert heading.inner_text().strip() == "Recommendation for You"

@pytest.mark.regression
def test_login_invalid_credentials_password_or_username(page: Page, base_url, username):
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    page.get_by_role("link", name="Log In").click()
    fill_input(page, "Enter your email or username", username)
    fill_input(page, "Enter your password", "wrong_password_123")

    page.get_by_role("button", name="Log In").click()

    # Untuk kasus ini, 'expect().to_be_visible()' sudah cukup sebagai jeda
    # karena kita tidak berpindah halaman, hanya menunggu pesan error muncul.
    error_message = page.locator("text=Email or Password incorrect")
    expect(error_message).to_be_visible(timeout=10000)
    assert error_message.inner_text().strip() == "Email or Password incorrect"

@pytest.mark.regression
def test_login_button_disabled_when_empty(page: Page, base_url):
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    page.get_by_role("link", name="Log In").click()
    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_disabled(timeout=12000)
    assert not login_button.is_enabled()

@pytest.mark.regression
def test_login_invalid_credentials(page: Page, base_url, username):
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    page.get_by_role("link", name="Log In").click()
    fill_input(page, "Enter your email or username", "adawrong")
    fill_input(page, "Enter your password", "wrong_password_123")

    page.get_by_role("button", name="Log In").click()

    # Untuk kasus ini, 'expect().to_be_visible()' sudah cukup sebagai jeda
    # karena kita tidak berpindah halaman, hanya menunggu pesan error muncul.
    error_message = page.locator("text=Email or Password incorrect")
    expect(error_message).to_be_visible(timeout=10000)
    assert error_message.inner_text().strip() == "Email or Password incorrect"

@pytest.mark.unit
def test_login_page_ui_elements(page: Page, base_url, take_screenshot):
    """
    Tes unit UI dengan fitur screenshot otomatis dari conftest.py.
    """
    # --- Alur Tes ---
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    take_screenshot("halaman_utama_dimuat")

    page.get_by_role("link", name="Log In").click()
    
    # Tunggu heading muncul untuk memastikan halaman login sudah siap
    expect(page.get_by_role("heading", name="Log In to Panorra")).to_be_visible(timeout=10000)
    take_screenshot("login_dimuat")

    # Verifikasi semua elemen di halaman login
    expect(page.get_by_placeholder("Enter your email or username")).to_be_visible(timeout=10000)
    expect(page.get_by_placeholder("Enter your password")).to_be_visible(timeout=10000)
    expect(page.get_by_text("Password", exact=True)).to_be_visible(timeout=10000)
    expect(page.get_by_text("Email/Username", exact=True)).to_be_visible(timeout=10000)
    expect(page.get_by_text("Forgot your password?")).to_be_visible(timeout=10000)
    expect(page.get_by_text("OR", exact=True)).to_be_visible(timeout=10000)
    expect(page.get_by_text("Need a Panorra account?")).to_be_visible(timeout=10000)

    iframe_locator = page.locator('iframe[title*="Google"]')
    expect(iframe_locator).to_be_visible(timeout=10000)
    
    google_iframe = page.frame_locator('iframe[title*="Google"]')
    expect(google_iframe.get_by_role("button")).to_be_visible(timeout=10000)
    
    # Ambil screenshot terakhir sebagai bukti semua elemen terlihat
    take_screenshot("semua_elemen_login_terlihat")