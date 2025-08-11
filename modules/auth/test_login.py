import pytest
from playwright.sync_api import Page


@pytest.mark.smoke
def test_login_success(page: Page):
    # 1. Buka halaman utama
    page.goto("https://panorra.com/")
    page.wait_for_load_state("networkidle")
    assert "Panorra" in page.title(), "Judul halaman tidak sesuai"

    # 2. Klik tombol "Log In"
    login_link = page.get_by_role("link", name="Log In")
    assert login_link.is_visible(), "Tombol Log In tidak ditemukan"
    login_link.click()

    # 3. Isi email & password valid
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    email_field.wait_for(state="visible")
    password_field.wait_for(state="visible")

    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")

    # 4. Klik tombol login
    login_button = page.get_by_role("button", name="Log In")
    assert login_button.is_enabled(), "Tombol Log In tidak aktif"
    login_button.click()

    # 5. Verifikasi heading halaman setelah login
    heading = page.wait_for_selector("role=heading[name='Recommendation for You']", timeout=10000)
    assert heading.is_visible(), "Login gagal, heading 'Recommendation for You' tidak ditemukan"


@pytest.mark.regression
def test_login_invalid_credentials(page: Page):
    page.goto("https://panorra.com/")
    page.wait_for_load_state("networkidle")
    assert "Panorra" in page.title()

    page.get_by_role("link", name="Log In").click()
    page.get_by_placeholder("Enter your email or username").fill("timbel@gmail.com")
    page.get_by_placeholder("Enter your password").fill("Ar_061204")
    page.get_by_role("button", name="Log In").click()

    error_message = page.wait_for_selector("text=Email or Password incorrect", timeout=5000)
    assert error_message.is_visible(), "Pesan error tidak muncul"


@pytest.mark.regression
def test_login_button_disabled_when_empty(page: Page):
    page.goto("https://panorra.com/")
    page.wait_for_load_state("networkidle")
    assert "Panorra" in page.title()

    page.get_by_role("link", name="Log In").click()
    login_button = page.get_by_role("button", name="Log In")
    assert login_button.is_disabled(), "Tombol Log In aktif padahal field kosong"


@pytest.mark.unit
def test_login_page_ui_elements(page: Page):
    page.goto("https://panorra.com/")
    page.wait_for_load_state("networkidle")

    # Klik tombol Log In
    login_link = page.get_by_role("link", name="Log In")
    assert login_link.is_visible(), "Tombol Log In tidak ditemukan"
    login_link.click()

    # Field email & password
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    email_field.wait_for(state="visible")
    password_field.wait_for(state="visible")

    # Cek label dan heading
    assert page.get_by_text("Password", exact=True).is_visible(), "Label Password tidak muncul"
    assert page.get_by_text("Email/Username", exact=True).is_visible(), "Label Email/Username tidak muncul"
    assert page.get_by_role("heading", name="Log In to Panorra").is_visible(), "Heading 'Log In to Panorra' tidak muncul"

    # Cek elemen div tertentu
    assert page.locator("div").filter(has_text="Log In to Panorra").first.is_visible(), \
        "Div dengan teks 'Log In to Panorra' tidak muncul"

    # Link dan teks tambahan
    assert page.get_by_text("Log In Forgot your password?").is_visible(), "Teks 'Forgot your password?' tidak muncul"
    assert page.get_by_text("OR", exact=True).is_visible(), "Teks 'OR' tidak muncul"
    assert page.get_by_text("Need a Panorra account?").is_visible(), "Teks 'Need a Panorra account?' tidak muncul"

    # Tombol login Google di dalam iframe
    google_iframe = page.frame_locator('iframe[title="Tombol Login dengan Google"]')
    assert google_iframe.get_by_role("button", name="Login dengan Google. Dibuka").is_visible(), \
        "Tombol login Google tidak muncul"
