import re
import pytest
from playwright.sync_api import Page

@pytest.mark.smoke
def test_logout_success(page: Page):
    page.goto("https://panorra.com/", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)
    assert re.search("Panorra", page.title()), "Title halaman tidak sesuai"

    # Klik tombol Log In
    login_link = page.get_by_role("link", name="Log In")
    assert login_link.is_visible(), "Tombol Log In tidak terlihat"
    login_link.click()
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(8000)

    # Isi email & password
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    assert email_field.is_visible(), "Kolom email tidak terlihat"
    assert password_field.is_visible(), "Kolom password tidak terlihat"
    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")
    page.wait_for_timeout(8000)

    # Klik tombol Log In
    login_button = page.get_by_role("button", name="Log In")
    assert login_button.is_enabled(), "Tombol Log In tidak aktif"
    login_button.click()
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(8000)

    # Buka menu header
    menu_button = page.get_by_role("button", name="header menu")
    assert menu_button.is_visible(), "Menu header tidak terlihat"
    menu_button.click()
    page.wait_for_timeout(8000)

    # Klik tombol Log Out
    logout_link = page.get_by_role("link", name=" Log Out")
    assert logout_link.is_visible(), "Tombol Log Out tidak terlihat"
    logout_link.click()
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(8000)

    # Pastikan halaman kembali ke rekomendasi
    heading = page.get_by_role("heading", name="Recommendation for You")
    assert heading.is_visible(), "Heading rekomendasi tidak muncul"
    page.wait_for_timeout(8000)

    # ✅ Tambahan: pastikan logout berhasil
    assert page.get_by_role("link", name="Log In").is_visible(), "Logout gagal: tombol Log In tidak muncul"
    assert "panorra.com" in page.url, f"Logout gagal: URL sekarang {page.url}"


@pytest.mark.regression
def test_without_logged_out(page: Page):
    page.goto("https://panorra.com/", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)

    # Klik tombol Log In
    login_link = page.get_by_role("link", name="Log In")
    assert login_link.is_visible(), "❌ Tombol Log In tidak terlihat"
    login_link.click()
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(8000)

    # Isi email & password
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    assert email_field.is_visible(), "❌ Kolom email tidak terlihat"
    assert password_field.is_visible(), "❌ Kolom password tidak terlihat"
    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")
    page.wait_for_timeout(8000)

    # Klik tombol Log In
    login_button = page.get_by_role("button", name="Log In")
    assert login_button.is_enabled(), "❌ Tombol Log In tidak aktif"
    login_button.click()
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(8000)

    # Pastikan user sudah login
    menu_button = page.get_by_role("button", name="header menu")
    assert menu_button.is_visible(), "❌ Gagal login: Menu header tidak terlihat"
    page.wait_for_timeout(8000)

    # Kembali ke halaman utama
    page.goto("https://panorra.com/")
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)

    # Klik menu header (tanpa logout)
    menu_button.click()
    page.wait_for_timeout(8000)

    # Pastikan heading "Recommendation for You" tetap ada
    heading = page.get_by_role("heading", name="Recommendation for You")
    assert heading.is_visible(), "❌ Heading 'Recommendation for You' tidak ditemukan setelah login"
    page.wait_for_timeout(8000)


@pytest.mark.unit
def test_unit_logout(page: Page):
    page.goto("https://panorra.com/", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)
    assert re.search("Panorra", page.title()), "Halaman utama tidak terbuka dengan benar"

    # Klik tombol Log In
    login_link = page.get_by_role("link", name="Log In")
    assert login_link.is_visible(), "Tombol Log In tidak ditemukan"
    login_link.click()
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(8000)

    # Isi email & password
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    assert email_field.is_visible(), "Field email tidak muncul"
    assert password_field.is_visible(), "Field password tidak muncul"
    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")
    page.wait_for_timeout(8000)

    # Klik tombol Log In
    login_button = page.get_by_role("button", name="Log In")
    assert login_button.is_enabled(), "Tombol Log In tidak aktif"
    login_button.click()
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(8000)

    # Pastikan halaman Recommendation terbuka
    heading = page.get_by_role("heading", name="Recommendation for You")
    assert heading.is_visible(), "Halaman Recommendation tidak muncul setelah login"
    page.wait_for_timeout(8000)

    # Klik menu header
    menu_button = page.get_by_role("button", name="header menu")
    assert menu_button.is_visible(), "Tombol menu header tidak ditemukan"
    menu_button.click()
    page.wait_for_timeout(8000)

    # Klik tombol Log Out
    logout_link = page.get_by_role("link", name=" Log Out")
    assert logout_link.is_visible(), "Tombol Log Out tidak ditemukan"
    logout_link.click()
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(8000)

    # Pastikan logout berhasil (tombol Log In muncul kembali)
    login_link_after = page.get_by_role("link", name="Log In")
    assert login_link_after.is_visible(), "Logout gagal, tombol Log In tidak muncul kembali"
    page.wait_for_timeout(8000)
