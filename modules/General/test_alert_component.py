import pytest
import re
from playwright.sync_api import Page, expect

# =====================================================================
# Constants for Timeout
# =====================================================================
LONG_TIMEOUT = 60000      # Timeout for page navigation and critical actions
MEDIUM_TIMEOUT = 15000    # Timeout for standard element verification

# =====================================================================
# Helper function for login
# =====================================================================
def login_user(page: Page, base_url: str, username: str, password: str):
    """Fungsi terpusat untuk menavigasi dan melakukan login."""
    print("Navigating to login page...")
    page.goto(base_url, timeout=LONG_TIMEOUT)
    page.get_by_role("link", name="Log In").click()
    
    print(f"Logging in with username: {username}...")
    page.get_by_role("textbox", name="Enter your email or username").fill(username)
    page.get_by_role("textbox", name="Enter your password").fill(password)
    page.get_by_role("button", name="Log In").click(timeout=LONG_TIMEOUT)
    
    # Verifikasi login berhasil
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=LONG_TIMEOUT)
    print("Login successful.")

# =====================================================================
# Combined Smoke Test for Success and Error Alerts
# =====================================================================

@pytest.mark.smoke
def test_success_and_error_alerts_flow(page: Page, base_url, username, password):
    """
    Memverifikasi alur alert sukses (block post) dan alert error (invalid profile edit)
    dalam satu smoke test.
    """
    # 1. Login ke aplikasi
    login_user(page, base_url, username, password)
    
    # --- BAGIAN 1: VERIFIKASI ALERT SUKSES ---
    print("\n--- Testing Success Alert: Blocking a Post ---")
    
    # 2. Klik postingan pertama di halaman utama
    print("Opening the first post...")
    page.locator('.d-block.w-100').first.click()
    
    # 3. Buka menu opsi dan blokir postingan
    print("Blocking the post...")
    page.locator('.flex-align-center > app-detail-menu > .header-more > #dropdownBasic1').click()
    page.get_by_role('link', name='Block Post').click()
    page.get_by_role('button', name='Confirm').click()
    
    # 4. Verifikasi alert sukses muncul
    print("Verifying success alert...")
    success_alert = page.get_by_text('Success Block Post')
    expect(success_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Success alert for blocking post verified.")

    # --- BAGIAN 2: VERIFIKASI ALERT ERROR ---
    print("\n--- Testing Error Alert: Invalid Profile Edit ---")

    # 5. Navigasi ke halaman Edit Profil
    print("Navigating to Edit Profile page...")
    page.get_by_role('button', name='header menu').click()
    page.get_by_text('Profile').click()
    page.get_by_role('button', name='Edit Profile').click()
    
    # 6. Masukkan nama yang terlalu panjang (tidak valid)
    print("Entering an invalid full name...")
    invalid_name = "Arnov Abdillah Rahman Paasdjahjskdakjsdbalsbd njang Banget Nama Nya"
    full_name_input = page.get_by_role('textbox', name='Enter full name')
    full_name_input.fill(invalid_name)
    
    # 7. Coba simpan profil
    page.get_by_role('button', name='Save Profile').click()
    
    # 8. Verifikasi alert error muncul
    print("Verifying error alert...")
    error_alert = page.get_by_text('Not valid fullname, fullname')
    expect(error_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Error alert for invalid full name verified.")

@pytest.mark.regression
def test_cancel_block_post_action(page: Page, base_url, username, password):
    """
    Memverifikasi bahwa pengguna dapat membatalkan aksi "Block Post"
    dari dialog konfirmasi.
    """
    # 1. Login ke aplikasi
    login_user(page, base_url, username, password)
    
    # 2. Klik postingan pertama untuk membukanya
    print("Opening the first post...")
    page.locator('.d-block.w-100').first.click()
    
    # 3. Buka menu opsi
    print("Opening post options menu...")
    menu_button = page.get_by_role("button", name="button menu")
    menu_button.click()
    
    # 4. Klik link "Block Post"
    print("Clicking 'Block Post'...")
    page.get_by_role('link', name='Block Post').click()
    
    # 5. Verifikasi bahwa dialog konfirmasi muncul (dengan mencari tombol "Cancel")
    cancel_button = page.get_by_role('button', name='Cancel')
    expect(cancel_button).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # 6. Klik tombol "Cancel" untuk membatalkan aksi
    print("Canceling the action...")
    cancel_button.click()
    
    # 7. Verifikasi bahwa dialog konfirmasi telah tertutup
    #    dan pengguna kembali ke state sebelumnya (menu opsi masih terlihat)
    print("Verifying the action was cancelled...")
    expect(cancel_button).to_be_hidden(timeout=MEDIUM_TIMEOUT)
    print("Block post action was successfully cancelled.")  

@pytest.mark.regression
def test_alert_does_not_appear_spontaneously(page: Page, base_url,username , password):
    """
    Memverifikasi bahwa alert tidak muncul tanpa pemicu dari pengguna.
    """
    login_user(page, base_url, username, password)
    
    generic_alert = page.locator('[role="alert"]')
    expect(generic_alert).to_be_hidden()
    print("Test passed. No spontaneous alert was found.")

@pytest.mark.regression
def test_no_action_on_confirmation_dialog(page: Page, base_url, username, password):
    """
    Memverifikasi bahwa sistem tetap menunggu dan tidak ada alert yang muncul
    jika pengguna tidak melakukan apa pun pada dialog konfirmasi "Block Post".
    """
    # 1. Login dan navigasi untuk memicu sebuah aksi
    login_user(page, base_url, username, password)
    page.locator('.d-block.w-100').first.click() # Klik postingan
    
    # 2. Buka menu dan klik "Block Post" untuk memunculkan dialog konfirmasi
    page.locator('.flex-align-center > app-detail-menu > .header-more > #dropdownBasic1').click()
    page.get_by_role('link', name='Block Post').click()
    
    # 3. Pastikan dialog konfirmasi (conditional page) sudah muncul
    print("Confirmation dialog is visible...")
    confirm_button = page.get_by_role('button', name='Confirm')
    expect(confirm_button).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # 4. Pengguna TIDAK MELAKUKAN APA PUN. Kita simulasikan dengan menunggu.
    print("User does nothing for 3 seconds...")
    page.wait_for_timeout(3000)
    
    # 5. Verifikasi bahwa kondisi halaman tidak berubah
    #    - Dialog konfirmasi harus tetap terlihat.
    #    - Alert sukses ("Success Block Post") TIDAK boleh muncul.
    print("Verifying that the state has not changed...")
    
    # Assertion 1: Pastikan dialog masih ada
    expect(confirm_button).to_be_visible()
    
    # Assertion 2: Pastikan alert sukses tidak muncul
    success_alert = page.get_by_text('Success Block Post')
    expect(success_alert).to_be_hidden()
    
    print("Test passed. System correctly waited for user input.")

@pytest.mark.unit
def test_login_ui_and_alerts_flow(page: Page, base_url, username, password):
    """
    Smoke test lengkap:
    1. Login.
    2. Memeriksa komponen UI.
    3. Memverifikasi alert sukses.
    4. Memverifikasi alert error.
    """
    # 1. LOGIN
    login_user(page, base_url, username, password)
    
    # 2. MEMERIKSA KOMPONEN UI SETELAH LOGIN
    print("\n--- Verifying Dashboard UI Components ---")
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible()
    expect(page.get_by_role("button", name="header menu")).to_be_visible()
    expect(page.get_by_role("link", name="banner")).to_be_visible()
    print("Dashboard UI components are visible.")
    
    # 3. VERIFIKASI ALERT SUKSES (BLOCK POST)
    print("\n--- Testing Success Alert: Blocking a Post ---")
    page.locator('.d-block.w-100').first.click()
    print("Opening the first post...")
    
    page.locator('.flex-align-center > app-detail-menu > .header-more > #dropdownBasic1').click()
    page.get_by_role('link', name='Block Post').click()
    page.get_by_role('button', name='Confirm').click()
    print("Post blocked.")
    
    success_alert = page.get_by_text('Success Block Post')
    expect(success_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Success alert verified.")

    # 4. VERIFIKASI ALERT ERROR (EDIT PROFIL)
    print("\n--- Testing Error Alert: Invalid Profile Edit ---")
    page.get_by_role('button', name='header menu').click()
    page.get_by_text('Profile').click()
    page.get_by_role('button', name='Edit Profile').click()
    print("Navigated to Edit Profile page.")
    
    invalid_name = "Nama Ini Jelas Terlalu Panjang Untuk Disimpan di Database dan Seharusnya Ditolak Oleh Sistem Validasi"
    page.get_by_role('textbox', name='Enter full name').fill(invalid_name)
    page.get_by_role('button', name='Save Profile').click()
    print("Attempting to save with invalid name...")
    
    error_alert = page.get_by_text('Not valid fullname, fullname')
    expect(error_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Error alert verified.")
    
    print("\nFull unit test completed successfully.")
    