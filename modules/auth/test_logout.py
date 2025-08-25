import pytest
import os
import re  # <-- Ditambahkan untuk menggunakan regular expression
from playwright.sync_api import Page, expect, BrowserContext

# =====================================================================
# Constants for Timeout
# Defined in one place for easy modification.
# =====================================================================
LONG_TIMEOUT = 30000      # For long processes like initial page loads
MEDIUM_TIMEOUT = 15000    # For standard element verification
SHORT_TIMEOUT = 5000      # For quick verifications

# =====================================================================
# Helper function for login
# =====================================================================
def login_user(page: Page, base_url: str, username: str, password: str):
    """Centralized function to navigate and perform login."""
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
# Final Test Suite
# =====================================================================

@pytest.mark.smoke
def test_logout_success(page: Page, base_url, username, password):
    """Verifies that the user can log out successfully."""
    login_user(page, base_url, username, password)
    
    # --- ALUR LOGOUT BARU ---
    page.get_by_role("button", name="header menu").click()
    # Menggunakan regex untuk mencocokkan "Log Out" dan mengabaikan ikon
    page.get_by_role("link", name=re.compile("Log Out")).click()
    # Mengklik tombol konfirmasi logout
    page.get_by_role("button", name="Log Out").click()
    # --- AKHIR ALUR LOGOUT BARU ---

    # Verify logout was successful
    expect(page.get_by_role("link", name="Log In")).to_be_visible(timeout=LONG_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_hidden(timeout=LONG_TIMEOUT)
    
    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_opening_menu_does_not_logout(page: Page, base_url, username, password):
    """Verifies that just opening the menu does not log the user out."""
    login_user(page, base_url, username, password)
    page.get_by_role("button", name="header menu").click()
    
    # Verify the menu appears and the user remains logged in
    # Selector diperbarui untuk lebih andal
    expect(page.get_by_role("link", name=re.compile("Log Out"))).to_be_visible(timeout=LONG_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible()
    
    page.wait_for_timeout(5000)


@pytest.mark.unit
def test_logout_button_functionality(page: Page, base_url, username, password, take_screenshot):
    """Verifies the functionality of the logout button and takes screenshots."""
    login_user(page, base_url, username, password)
    take_screenshot("login_successful")
    
    # --- ALUR LOGOUT BARU ---
    page.get_by_role("button", name="header menu").click()
    take_screenshot("header_menu_visible")
    
    # Klik link logout di menu
    logout_link = page.get_by_role("link", name=re.compile("Log Out"))
    expect(logout_link).to_be_visible(timeout=LONG_TIMEOUT)
    logout_link.click()

    # Klik tombol konfirmasi logout yang muncul
    logout_confirmation_button = page.get_by_role("button", name="Log Out")
    expect(logout_confirmation_button).to_be_visible(timeout=SHORT_TIMEOUT)
    logout_confirmation_button.click()
    # --- AKHIR ALUR LOGOUT BARU ---
    
    expect(page.get_by_role("link", name="Log In")).to_be_visible(timeout=LONG_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_hidden(timeout=LONG_TIMEOUT)
    take_screenshot("logout_successful")

import os # Pastikan modul 'os' sudah di-import di bagian atas file Anda

# ... (kode lain di file Anda) ...

@pytest.mark.regression
def test_session_persists_after_browser_close(browser: BrowserContext, page: Page, base_url, username, password):
    """
    Verifies that the login session persists after the browser is closed and reopened,
    now with custom HTTP headers in the new context.
    """
    storage_state_path = "state.json"
    
    # 1. Login seperti biasa dan simpan state sesi
    login_user(page, base_url, username, password)
    page.context.storage_state(path=storage_state_path)
    page.context.close()
    
    # 2. Siapkan argumen untuk browser context yang baru
    #    Ini akan mencakup state sesi yang disimpan DAN custom headers
    context_args = {
        "storage_state": storage_state_path,
        "extra_http_headers": {
            "Access-Code": os.getenv("ACCESS_CODE", "default-code-if-not-set") 
            # Menggunakan os.getenv untuk mengambil ACCESS_CODE dari environment variable
        }
    }
    
    # Tambahkan logika untuk video jika diperlukan (opsional, sesuai contoh Anda)
    # is_flow_test = False # Ganti dengan logika Anda untuk menentukan ini
    # if is_flow_test:
    #     context_args["record_video_dir"] = "/path/to/videos"

    # 3. Buat context dan page baru menggunakan argumen yang sudah disiapkan
    new_context = browser.new_context(**context_args)
    new_page = new_context.new_page()
    new_page.goto(base_url, timeout=LONG_TIMEOUT)

    # 4. Verifikasi bahwa pengguna masih dalam keadaan login
    expect(new_page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=LONG_TIMEOUT)
    
    # 5. Lakukan pembersihan seperti biasa
    new_context.close()
    if os.path.exists(storage_state_path):
        os.remove(storage_state_path)