import re
import pytest
from playwright.sync_api import Page, sync_playwright

@pytest.mark.smoke
def test_logout_success(page: Page):
    # Buka halaman utama
    page.goto("https://panorra.com/", timeout=10000)
    page.wait_for_load_state("domcontentloaded", timeout=10000)
    page.wait_for_timeout(10000)

    # Klik tombol Log In
    login_link = page.get_by_role("link", name="Log In")
    assert login_link.is_visible(), "Tombol Log In tidak terlihat"
    login_link.click()
    page.wait_for_timeout(10000)

    # Isi email & password
    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    assert email_field.is_visible(), "Kolom email tidak terlihat"
    assert password_field.is_visible(), "Kolom password tidak terlihat"
    email_field.fill("arnov@grr.la")
    page.wait_for_timeout(10000)
    password_field.fill("Ar_061204")
    page.wait_for_timeout(10000)

    # Klik tombol Log In
    login_button = page.get_by_role("button", name="Log In")
    assert login_button.is_enabled(), "Tombol Log In tidak aktif"
    login_button.click()
    page.wait_for_timeout(10000)

    # Buka menu header
    menu_button = page.get_by_role("button", name="header menu")
    assert menu_button.is_visible(), "Menu header tidak terlihat"
    menu_button.click()
    page.wait_for_timeout(10000)

    # Klik tombol Log Out
    logout_link = page.get_by_role("link", name=" Log Out")
    assert logout_link.is_visible(), "Tombol Log Out tidak terlihat"
    logout_link.click()
    page.wait_for_timeout(10000)

    # Assertion tambahan
    heading = page.get_by_role("heading", name="Recommendation for You")
    assert heading.is_visible(), "Halaman tidak kembali ke Recommendation for You"
    page.wait_for_timeout(10000)

    login_link_after_logout = page.get_by_role("link", name="Log In")
    assert login_link_after_logout.is_visible(), "Tombol Log In tidak muncul setelah logout"


@pytest.mark.regression
def test_visible_logged_out():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://panorra.com/", timeout=20000)
        page.wait_for_timeout(10000)

        login_link = page.get_by_role("link", name="Log In")
        assert login_link.is_visible(), "Tombol Log In tidak terlihat"
        login_link.click()
        page.wait_for_timeout(10000)

        email_field = page.get_by_role("textbox", name="Enter your email or username")
        assert email_field.is_visible(), "Kolom email tidak terlihat"
        email_field.fill("arnov@grr.la")
        page.wait_for_timeout(10000)

        password_field = page.get_by_role("textbox", name="Enter your password")
        assert password_field.is_visible(), "Kolom password tidak terlihat"
        password_field.fill("Ar_061204")
        page.wait_for_timeout(10000)

        login_button = page.get_by_role("button", name="Log In")
        assert login_button.is_enabled(), "Tombol Log In tidak aktif"
        login_button.click()
        page.wait_for_timeout(10000)

        header_menu_button = page.get_by_role("button", name="header menu")
        assert header_menu_button.is_visible(), "Menu header tidak terlihat setelah login"
        page.wait_for_timeout(10000)

        recommendation_heading = page.get_by_role("heading", name="Recommendation for You")
        assert recommendation_heading.is_visible(), 'Tulisan "Recommendation for You" tidak terlihat setelah login'
        page.wait_for_timeout(10000)

        page.screenshot(path="screenshots/regression/recommendation_page_passed.png")
        browser.close()


@pytest.mark.unit
def test_logout_unit():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://panorra.com/", timeout=20000)
        page.wait_for_timeout(10000)

        login_link = page.get_by_role("link", name="Log In")
        assert login_link.is_visible(), "Tombol Log In tidak terlihat"
        login_link.click()
        page.wait_for_timeout(10000)

        email_field = page.get_by_role("textbox", name="Enter your email or username")
        assert email_field.is_visible(), "Kolom email tidak terlihat"
        email_field.fill("arnov@grr.la")
        page.wait_for_timeout(10000)

        password_field = page.get_by_role("textbox", name="Enter your password")
        assert password_field.is_visible(), "Kolom password tidak terlihat"
        password_field.fill("Ar_061204")
        page.wait_for_timeout(10000)

        login_button = page.get_by_role("button", name="Log In")
        assert login_button.is_enabled(), "Tombol Log In tidak aktif"
        login_button.click()
        page.wait_for_timeout(10000)

        header_menu_button = page.get_by_role("button", name="header menu")
        assert header_menu_button.is_visible(), "Menu header tidak terlihat setelah login"
        page.wait_for_timeout(10000)

        header_menu_button.click()
        page.wait_for_timeout(10000)

        logout_button = page.get_by_role("link", name=" Log Out")
        assert logout_button.is_visible(), "Tombol Log Out tidak terlihat"
        logout_button.click()
        page.wait_for_timeout(10000)

        recommendation_heading = page.get_by_role("heading", name="Recommendation for You")
        assert recommendation_heading.is_visible(), 'Tulisan "Recommendation for You" tidak terlihat setelah logout'
        page.wait_for_timeout(10000)

        page.screenshot(path="screenshots/unit/logout_passed.png")
        browser.close()
