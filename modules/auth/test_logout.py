import re
import pytest
from playwright.sync_api import Page, expect

# Tes untuk memastikan proses logout berhasil
@pytest.mark.smoke
def test_logout_success(page: Page, base_url, username, password):
    # Tahap Login
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("networkidle")
    page.get_by_role("link", name="Log In").click()

    page.get_by_placeholder("Enter your email or username").fill(username)
    page.get_by_placeholder("Enter your password").fill(password)
    page.get_by_role("button", name="Log In").click()
    
    # Tunggu hingga login berhasil dengan "jeda cerdas"
    page.wait_for_load_state("networkidle", timeout=20000)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=20000)

    # Tahap Logout
    page.get_by_role("button", name="header menu").click()
    page.locator('a:has-text("Log Out")').click()

    # Tunggu hingga proses logout selesai dengan "jeda cerdas"
    page.wait_for_load_state("networkidle", timeout=20000)

    # --- LOGIKA ASSERTION YANG LENGKAP DAN BENAR ---
    
    # 1. Pastikan elemen dashboard (heading) sudah HILANG.
    heading_after_logout = page.get_by_role("heading", name="Recommendation for You")
    expect(heading_after_logout).to_be_hidden(timeout=10000)
    
    # 2. Pastikan tombol "Log In" MUNCUL KEMBALI (ini adalah assertion yang sebelumnya hilang).
    #    Ini adalah bukti terkuat bahwa pengguna sudah benar-benar logout.
    login_link_after_logout = page.get_by_role("link", name="Log In")
    expect(login_link_after_logout).to_be_visible(timeout=10000)
    
    # 3. Pastikan URL kembali ke halaman utama.
    expect(page).to_have_url(re.compile(r".*panorra.com/?$"), timeout=5000)

#-------------------------------------------------------------------------------------------------------------------

# Tes untuk memastikan pengguna tetap login (session tetap aktif)
@pytest.mark.regression
def test_user_stays_logged_in(page: Page, base_url, username, password):
    # Tahap Login
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("networkidle")
    page.get_by_role("link", name="Log In").click()

    page.get_by_placeholder("Enter your email or username").fill(username)
    page.get_by_placeholder("Enter your password").fill(password)
    page.get_by_role("button", name="Log In").click()

    # --- JEDA PAKSA 6 DETIK DITAMBAHKAN ---
    page.wait_for_timeout(5000)

    # Tunggu hingga login berhasil
    page.wait_for_load_state("networkidle")

    # Assertion: Cek elemen setelah login
    expect(page.get_by_role("button", name="header menu")).to_be_visible(timeout=20000)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=20000)
    
    # Navigasi ke halaman lain dan kembali untuk memastikan session tidak hilang
    page.goto(f"{base_url}/about")
    page.wait_for_load_state("networkidle")
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Periksa kembali elemen login setelah navigasi
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=20000)

#-------------------------------------------------------------------------------------------------------------------

# Tes unit untuk fungsionalitas tombol logout
@pytest.mark.unit
def test_logout_button_functionality(page: Page, base_url, username, password, take_screenshot):
    # Tahap Login
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("networkidle")
    page.get_by_role("link", name="Log In").click()

    page.get_by_placeholder("Enter your email or username").fill(username)
    page.get_by_placeholder("Enter your password").fill(password)
    page.get_by_role("button", name="Log In").click()
    
    # --- JEDA PAKSA 6 DETIK DITAMBAHKAN ---
    page.wait_for_timeout(5000)
    
    # Tunggu hingga login berhasil
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("button", name="header menu")).to_be_visible(timeout=20000)
    take_screenshot("login_berhasil")
    # Tahap Logout
    page.get_by_role("button", name="header menu").click()
    take_screenshot("header_menu_terlihat")
    page.locator('a:has-text("Log Out")').click()
    take_screenshot("logout_terlihat")

    # --- JEDA PAKSA 6 DETIK DITAMBAHKAN ---
    page.wait_for_timeout(5000)

    page.wait_for_load_state("networkidle")
    take_screenshot("logout_berhasil")
    # --- LOGIKA ASSERTION ---
    login_link_after_logout = page.get_by_role("link", name="Log In")
    take_screenshot("login_setelah_logout_terlihat")
    expect(login_link_after_logout).to_be_visible(timeout=10000)