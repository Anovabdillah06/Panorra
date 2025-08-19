import pytest
import re
from playwright.sync_api import Page, expect

# =====================================================================
# Constants for Timeout
# =====================================================================
LONG_TIMEOUT = 60000      # Timeout for page navigation
MEDIUM_TIMEOUT = 15000    # Timeout for element verification

# =====================================================================
# Test using original locators
# =====================================================================

@pytest.mark.smoke
def test_app_store_links_with_original_locators(page: Page, base_url):
    """
    Verifies the app store links using the original locators from the script.
    """
    # 1. Navigate to the homepage
    page.goto(base_url, timeout=LONG_TIMEOUT)

    # --- VERIFIKASI LINK PERTAMA (GOOGLE PLAY) ---
    print("Verifying the first link (Google Play)...")
    
    # PERBAIKAN: Hapus tanda kurung dari .first
    first_link_locator = page.get_by_role("list").filter(has_text=re.compile(r'^$')).get_by_role("link").first
    expect(first_link_locator).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    with page.context.expect_event("page") as new_page_info:
        first_link_locator.click()
        
    google_play_page = new_page_info.value
    google_play_page.wait_for_load_state(timeout=LONG_TIMEOUT)
    
    # Verifikasi konten di halaman Google Play
    expect(google_play_page.get_by_text("Panorra", exact=True)).to_be_visible(timeout=MEDIUM_TIMEOUT)
    google_play_page.close()
    print("First link verified successfully.")

    # --- VERIFIKASI LINK KEDUA (APPLE APP STORE) ---
    print("\nVerifying the second link (Apple App Store)...")

    # Menggunakan locator asli dari skrip Anda, disesuaikan untuk Python
    # .nth(1) sudah benar karena merupakan metode/fungsi
    second_link_locator = page.get_by_role("list").filter(has_text=re.compile(r'^$')).get_by_role("link").nth(1)
    expect(second_link_locator).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    with page.context.expect_event("page") as new_page_info:
        second_link_locator.click()
        
    app_store_page = new_page_info.value
    app_store_page.wait_for_load_state(timeout=LONG_TIMEOUT)
    
    # Verifikasi konten di halaman Apple App Store
    expect(app_store_page.get_by_role("heading", name="Panorra 4+")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    app_store_page.close()
    print("Second link verified successfully.")

@pytest.mark.regression
def test_no_click_on_find_us_on_does_not_redirect(page: Page, base_url):
    """
    Memverifikasi bahwa pengguna tidak diarahkan ke app store jika mereka
    hanya melihat halaman dan tidak mengklik link di "Find Us On".
    (Skenario Positive False)
    """
    # 1. Buka halaman utama
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 2. Verifikasi bahwa panel navigasi kiri sudah terlihat (sesuai permintaan Anda)
    print("Verifying that the left navigation panel is visible...")
    left_nav_panel = page.locator("div", has_text=re.compile(r'RecentJust for YouNearest')).nth(2)
    expect(left_nav_panel).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # 5. Verifikasi bahwa URL halaman tetap sama
    expect(page).to_have_url(base_url)
    print("Test passed. No redirect was triggered.")

@pytest.mark.regression
def test_feature_load_failure_does_not_auto_redirect(page: Page, base_url):
    """
    Memverifikasi bahwa jika fitur "Find Us On" gagal dimuat, sistem
    TIDAK melakukan redirect otomatis (menguji terhadap bug).
    (Skenario Negative False)
    """
    # 1. Simulasikan kondisi gagal muat dengan memblokir API atau script
    #    yang memuat fitur "Find Us On".
    #    Ganti '**/api/find-us-on*' dengan path API yang sebenarnya.
    print("Simulating a failure to load the 'Find Us On' feature...")
    page.route("**/api/find-us-on*", lambda route: route.abort())
    
    # 2. Buka halaman utama
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 3. Tunggu sebentar untuk memberi kesempatan jika ada redirect otomatis
    page.wait_for_timeout(3000)
    
    # 4. Verifikasi utama: Pastikan URL halaman TIDAK berubah.
    #    Tes ini akan berhasil jika TIDAK ada redirect.
    expect(page).to_have_url(base_url)
    print("Test passed. The system correctly did not redirect on feature load failure.")

@pytest.mark.unit
def test_homepage_elements_are_visible(page: Page, base_url):
    """
    Verifies that key elements on the homepage are visible, including those
    that require scrolling. This test uses specific locators as requested.
    """
    # 1. Navigate to the homepage
    page.goto(base_url, timeout=LONG_TIMEOUT)

    # 2. Verify elements visible on initial load (Above the Fold)
    print("Verifying elements visible on initial load...")

    # Verifikasi panel navigasi kiri menggunakan locator dari Anda
    left_nav_panel = page.locator("div", has_text=re.compile(r'RecentJust for YouNearest')).nth(2)
    expect(left_nav_panel).to_be_visible(timeout=MEDIUM_TIMEOUT)

    # Verifikasi heading "Recommendation for You"
    recommendation_heading = page.get_by_role("heading", name="Recommendation for You")
    expect(recommendation_heading).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    print("Initial elements are visible.")

    # 3. Scroll to the bottom of the page to find the footer elements
    print("Scrolling to the bottom of the page...")
    # Cara sederhana dan efektif untuk scroll ke paling bawah
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    
    # 4. Verify elements visible after scrolling (Below the Fold)
    print("Verifying elements visible after scrolling...")
    
    # Verifikasi heading "Find Us On"
    find_us_on_heading = page.get_by_role("heading", name="Find Us On")
    expect(find_us_on_heading).to_be_visible(timeout=MEDIUM_TIMEOUT)

    # Verifikasi link download pertama (Google Play) menggunakan locator asli
    first_download_link = page.get_by_role("list").filter(has_text=re.compile(r'^$')).get_by_role("link").first
    expect(first_download_link).to_be_visible(timeout=MEDIUM_TIMEOUT)

    # Verifikasi link download kedua (App Store) menggunakan locator asli
    second_download_link = page.get_by_role("list").filter(has_text=re.compile(r'^$')).get_by_role("link").nth(1)
    expect(second_download_link).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    print("All key elements have been successfully verified.")  
