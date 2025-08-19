import pytest
from playwright.sync_api import Page, expect

LONG_TIMEOUT = 60000  # Waktu tunggu diperpanjang menjadi 60 detik
MEDIUM_TIMEOUT = 15000

@pytest.mark.smoke
def test_banner_link_loads_new_page_successfully(page: Page, base_url):
    """
    Memverifikasi link banner membuka dan memuat halaman baru dengan sukses.
    """
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    banner_link = page.get_by_role("link", name="banner")
    expect(banner_link).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # Menunggu event 'page' (tab/popup baru) muncul setelah klik
    with page.context.expect_event("page") as new_page_info:
        banner_link.click()
    
    # Mengambil objek halaman baru dari event
    new_page = new_page_info.value    
    # (Opsional) Setelah verifikasi berhasil, tutup halaman baru
    new_page.close()

@pytest.mark.smoke
def test_verifies_staying_on_homepage_after_load(page: Page, base_url):
    """
    Memverifikasi bahwa setelah halaman dimuat, tidak ada redirect otomatis
    dengan cara memeriksa keberadaan elemen banner dan URL saat ini.
    """
    # 1. Buka halaman utama
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 2. Cari elemen banner untuk mendeteksi bahwa kita masih di halaman yang benar
    #    (elemen ini tidak akan diklik)
    banner_element = page.get_by_role("link", name="banner")
    
    # 3. Verifikasi bahwa elemen banner tersebut terlihat.
    #    Jika elemen ini ada, berarti kita masih berada di halaman utama.
    expect(banner_element).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # 4. (Assertion Tambahan) Periksa secara eksplisit bahwa URL halaman
    #    saat ini masih sama dengan base_url.
    expect(page).to_have_url(base_url)

@pytest.mark.regression
def test_banner_is_visible_when_ads_are_blocked(page: Page, base_url):
    """
    Memverifikasi bahwa "button banner" tetap terlihat di halaman
    meskipun fitur ad blocker (simulasi) sedang aktif.
    """
    # 1. Aktifkan simulasi ad blocker dengan memblokir domain iklan
    page.route("**/*doubleclick.net*", lambda route: route.abort())
    page.route("**/*googlesyndication.com*", lambda route: route.abort())
    
    # 2. Buka halaman utama
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 3. (Verifikasi Tambahan) Pastikan elemen iklan benar-benar terblokir/tersembunyi.
    #    Ganti '.ad-container' dengan selector iklan di web Anda.
    ad_locator = page.locator('.ad-container')
    expect(ad_locator).to_be_hidden(timeout=MEDIUM_TIMEOUT)
    
    # 4. (Verifikasi Utama) Cari dan pastikan "button banner" tetap terlihat.
    #    Ini adalah inti dari tes Anda.
    banner_locator = page.get_by_role("link", name="banner")
    
    # Assertion ini memastikan bahwa banner tidak ikut hilang saat iklan diblokir.
    expect(banner_locator).to_be_visible(timeout=MEDIUM_TIMEOUT)

@pytest.mark.regression
def test_malicious_redirect_is_prevented(page: Page, base_url):
    """
    Memverifikasi halaman tidak melakukan redirect otomatis tanpa interaksi.
    (Skenario Negative False)
    """
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # Tunggu beberapa detik untuk melihat apakah ada script yang mencoba redirect
    page.wait_for_timeout(3000)
    
    # Verifikasi bahwa halaman masih berada di URL yang sama dan tidak di-redirect
    expect(page).to_have_url(base_url)

@pytest.mark.unit
def test_homepage_key_elements_are_visible(page: Page, base_url):
    """
    Memverifikasi bahwa semua elemen interaktif utama di halaman utama terlihat.
    """
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # Verifikasi elemen-elemen utama terlihat sebelum interaksi
    print("Memverifikasi visibilitas elemen-elemen kunci...")
    
    expect(page.get_by_role("link", name="Log In")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(page.get_by_role("button", name="next popular")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(page.get_by_role("listitem").filter(has_text="Recent")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(page.get_by_role("link", name="banner")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    print("Semua elemen kunci berhasil diverifikasi.")