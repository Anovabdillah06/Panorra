import pytest
from playwright.sync_api import Page

@pytest.mark.smoke
def test_login_success(page: Page):
    # 1. Buka halaman utama
    page.goto("https://panorra.com/")
    assert "Panorra" in page.title(), "Judul halaman tidak sesuai"

    # 2. Klik tombol "Log In"
    login_link = page.get_by_role("link", name="Log In")
    assert login_link.is_visible(), "Tombol Log In tidak ditemukan"
    login_link.click()

    # 3. Isi email & password valid
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    assert email_field.is_visible(), "Field email tidak terlihat"
    assert password_field.is_visible(), "Field password tidak terlihat"

    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")

    # 4. Klik tombol login
    login_button = page.get_by_role("button", name="Log In")
    assert login_button.is_enabled(), "Tombol Log In tidak aktif"
    login_button.click()

    # 5. Tunggu hingga elemen utama halaman setelah login muncul
    heading = page.wait_for_selector("role=heading[name='Recommendation for You']", timeout=10000)
    assert heading.is_visible(), "Login gagal, heading 'Recommendation for You' tidak ditemukan"

@pytest.mark.regression
def test_login_invalid_credentials(page: Page):
    # 1. Buka halaman utama
    page.goto("https://panorra.com/")
    assert "Panorra" in page.title(), "Judul halaman tidak sesuai"

    # 2. Klik tombol "Log In"
    page.get_by_role("link", name="Log In").click()

    # 3. Isi email & password salah
    page.get_by_placeholder("Enter your email or username").fill("timbel@gmail.com")
    page.get_by_placeholder("Enter your password").fill("Ar_061204")

    # 4. Klik tombol login
    page.get_by_role("button", name="Log In").click()

    # 5. Verifikasi pesan error
    error_message = page.get_by_text("Email or Password incorrect")
    assert error_message.is_visible(), "Pesan error tidak muncul"


@pytest.mark.regression
def test_login_button_disabled_when_empty(page: Page):
    # 1. Buka halaman utama
    page.goto("https://panorra.com/")
    assert "Panorra" in page.title(), "Judul halaman tidak sesuai"

    # 2. Klik tombol "Log In"
    page.get_by_role("link", name="Log In").click()

    # 3. Pastikan tombol login disable saat field kosong
    login_button = page.get_by_role("button", name="Log In")
    assert login_button.is_disabled(), "Tombol Log In aktif padahal field kosong"

@pytest.mark.unit
def test_login_page_ui_elements(page: Page):
    # 1. Buka halaman utama
    page.goto("https://panorra.com/")
    page.wait_for_load_state("networkidle")

    # 2. Klik tombol Log In
    login_link = page.get_by_role("link", name="Log In")
    assert login_link.is_visible(), "Tombol Log In tidak ditemukan"
    login_link.click()

    # 3. Klik field email & password lalu cek validasi error muncul
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")

    assert email_field.is_visible(), "Field email tidak terlihat"
    assert password_field.is_visible(), "Field password tidak terlihat"

    email_field.click()
    password_field.click()


    # 4. Cek label dan heading
    assert page.get_by_text("Password", exact=True).is_visible(), "Label Password tidak muncul"
    assert page.get_by_text("Email/Username", exact=True).is_visible(), "Label Email/Username tidak muncul"
    assert page.get_by_role("heading", name="Log In to Panorra").is_visible(), \
        "Heading 'Log In to Panorra' tidak muncul"

    # 5. Cek elemen div tertentu
    assert page.locator("div").filter(has_text="Log In to Panorra").first.is_visible(), \
        "Div dengan teks 'Log In to Panorra' tidak muncul"

    # 7. Cek link dan teks tambahan
    assert page.get_by_text("Log In Forgot your password?").is_visible(), \
        "Teks 'Forgot your password?' tidak muncul"
    assert page.get_by_text("OR", exact=True).is_visible(), "Teks 'OR' tidak muncul"
    assert page.get_by_text("Need a Panorra account?").is_visible(), \
        "Teks 'Need a Panorra account?' tidak muncul"

    # 8. Cek tombol login Google di dalam iframe
    google_iframe = page.frame_locator('iframe[title="Tombol Login dengan Google"]')
    assert google_iframe.get_by_role("button", name="Login dengan Google. Dibuka").is_visible(), \
        "Tombol login Google tidak muncul"