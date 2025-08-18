import pytest
import os
import re
from playwright.sync_api import Page, expect, BrowserContext

# =====================================================================
# Konstanta untuk Timeout
# Didefinisikan di satu tempat agar mudah diubah.
# =====================================================================
LONG_TIMEOUT = 30000    # Untuk proses yang lama seperti memuat halaman pertama kali
MEDIUM_TIMEOUT = 15000  # Untuk verifikasi elemen standar
SHORT_TIMEOUT = 5000    # Untuk verifikasi cepat

# =====================================================================
# Helper function untuk login
# =====================================================================
def login_user(page: Page, base_url: str, username: str, password: str):
    """Fungsi terpusat untuk menavigasi dan melakukan login."""
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=MEDIUM_TIMEOUT)
    login_link.click()
    
    page.get_by_placeholder("Enter your email or username").fill(username)
    page.get_by_placeholder("Enter your password").fill(password)
    page.get_by_role("button", name="Log In").click()
    
    dashboard_heading = page.get_by_role("heading", name="Recommendation for You")
    expect(dashboard_heading).to_be_visible(timeout=LONG_TIMEOUT)

# =====================================================================
# Kumpulan Tes Final
# =====================================================================

@pytest.mark.smoke
def test_logout_success(page: Page, base_url, username, password):
    """Memverifikasi bahwa pengguna dapat logout dengan sukses."""
    login_user(page, base_url, username, password)
    
    page.get_by_role("button", name="header menu").click()
    page.locator('a:has-text("Log Out")').click()

    # Verifikasi logout berhasil
    expect(page.get_by_role("link", name="Log In")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_hidden(timeout=SHORT_TIMEOUT)

# @pytest.mark.regression
# def test_shows_reconnect_page_when_offline(page: Page, base_url, username, password):
#     """Memverifikasi halaman 'reconnect' muncul saat koneksi terputus."""
#     try:
#         login_user(page, base_url, username, password)
#         page.context.set_offline(True)
        
#         page.get_by_role("button", name="header menu").click()
#         logout_link = page.locator('a:has-text("Log Out")')
#         expect(logout_link).to_be_visible(timeout=SHORT_TIMEOUT)
#         logout_link.click(no_wait_after=True)
        
#         # Verifikasi halaman offline muncul
#         expect(page.get_by_role("heading", name="Connect with Internet")).to_be_visible(timeout=MEDIUM_TIMEOUT)
#         expect(page.get_by_role("button", name="Retry")).to_be_visible(timeout=MEDIUM_TIMEOUT)
#     finally:
#         # Menjamin koneksi kembali normal setelah tes selesai
#         page.context.set_offline(False)

@pytest.mark.regression
def test_opening_menu_does_not_logout(page: Page, base_url, username, password):
    """Memverifikasi bahwa hanya membuka menu tidak me-logout pengguna."""
    login_user(page, base_url, username, password)
    page.get_by_role("button", name="header menu").click()
    
    # Verifikasi menu muncul dan pengguna tetap login
    expect(page.locator('a:has-text("Log Out")')).to_be_visible(timeout=SHORT_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible()

@pytest.mark.unit
def test_logout_button_functionality(page: Page, base_url, username, password, take_screenshot):
    """Memverifikasi fungsionalitas tombol logout dan mengambil screenshot."""
    login_user(page, base_url, username, password)
    take_screenshot("login_berhasil")
    
    page.get_by_role("button", name="header menu").click()
    take_screenshot("header_menu_terlihat")
    
    logout_link = page.locator('a:has-text("Log Out")')
    expect(logout_link).to_be_visible(timeout=SHORT_TIMEOUT)
    logout_link.click()
    
    expect(page.get_by_role("link", name="Log In")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_hidden(timeout=SHORT_TIMEOUT)
    take_screenshot("logout_berhasil")

@pytest.mark.regression
def test_session_persists_after_browser_close(browser: BrowserContext, page: Page, base_url, username, password):
    """Memverifikasi sesi login tetap ada setelah browser ditutup dan dibuka kembali."""
    storage_state_path = "state.json"
    
    login_user(page, base_url, username, password)
    page.context.storage_state(path=storage_state_path)
    page.context.close()
    
    # Buka konteks baru dengan state yang tersimpan
    new_context = browser.new_context(storage_state=storage_state_path)
    new_page = new_context.new_page()
    new_page.goto(base_url, timeout=LONG_TIMEOUT)

    # Verifikasi masih dalam keadaan login
    expect(new_page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(new_page.get_by_role("link", name="Log In")).to_be_hidden(timeout=SHORT_TIMEOUT)
    
    new_context.close()
    if os.path.exists(storage_state_path):
        os.remove(storage_state_path)

    #selesai