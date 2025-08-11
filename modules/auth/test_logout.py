import pytest
from playwright.sync_api import Page, sync_playwright
from playwright.async_api import async_playwright


# =============================
# HELPER FUNCTIONS
# =============================
def login(page: Page, email: str, password: str):
    page.goto("https://panorra.com/", timeout=20000)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    login_link = page.get_by_role("link", name="Log In")
    assert login_link.is_visible(), "Tombol Log In tidak terlihat"
    login_link.click()
    page.wait_for_timeout(1000)

    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    assert email_field.is_visible(), "Kolom email tidak terlihat"
    assert password_field.is_visible(), "Kolom password tidak terlihat"
    email_field.fill(email)
    password_field.fill(password)

    login_button = page.get_by_role("button", name="Log In")
    assert login_button.is_enabled(), "Tombol Log In tidak aktif"
    login_button.click()
    page.wait_for_timeout(2000)


def logout(page: Page):
    menu_button = page.get_by_role("button", name="header menu")
    assert menu_button.is_visible(), "Menu header tidak terlihat"
    menu_button.click()
    page.wait_for_timeout(1000)

    logout_link = page.get_by_role("link", name=" Log Out")
    assert logout_link.is_visible(), "Tombol Log Out tidak terlihat"
    logout_link.click()
    page.wait_for_timeout(2000)


# =============================
# SMOKE TEST
# =============================
@pytest.mark.smoke
def test_logout_success(page: Page):
    login(page, "arnov@grr.la", "Ar_061204")
    logout(page)

    heading = page.get_by_role("heading", name="Recommendation for You")
    assert heading.is_visible(), "Tidak kembali ke halaman utama"
    assert page.get_by_role("link", name="Log In").is_visible(), "Tombol Log In tidak muncul setelah logout"


# =============================
# REGRESSION TEST
# =============================
@pytest.mark.regression
def test_logout_regression():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        login(page, "arnov@grr.la", "Ar_061204")
        logout(page)

        assert page.get_by_role("link", name="Log In").is_visible(), "Tombol Log In hilang"
        page.screenshot(path="screenshots/regression/logout_passed.png")

        browser.close()


# =============================
# UNIT TEST
# =============================
@pytest.mark.unit
def test_logout_unit():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        login(page, "arnov@grr.la", "Ar_061204")
        logout(page)

        heading = page.get_by_role("heading", name="Recommendation for You")
        assert heading.is_visible(), "Tidak kembali ke halaman utama"
        page.screenshot(path="screenshots/unit/logout_passed.png")

        browser.close()
