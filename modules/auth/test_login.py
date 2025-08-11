import re
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_login_success(page: Page):
    page.goto("https://panorra.com/", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    expect(page).to_have_title(re.compile("Panorra"), timeout=15000)

    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=20000)
    login_link.click()

    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    expect(email_field).to_be_visible(timeout=10000)
    expect(password_field).to_be_visible(timeout=10000)

    email_field.fill("arnov@grr.la")
    password_field.fill("Ar_061204")

    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_enabled(timeout=5000)
    login_button.click()

    heading = page.get_by_role("heading", name="Recommendation for You")
    expect(heading).to_be_visible(timeout=30000)


@pytest.mark.regression
def test_login_invalid_credentials(page: Page):
    page.goto("https://panorra.com/", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    expect(page).to_have_title(re.compile("Panorra"), timeout=15000)

    page.get_by_role("link", name="Log In").click()
    page.get_by_placeholder("Enter your email or username").fill("timbel@gmail.com")
    page.get_by_placeholder("Enter your password").fill("Ar_061204")
    page.get_by_role("button", name="Log In").click()

    error_message = page.locator("text=Email or Password incorrect")
    expect(error_message).to_be_visible(timeout=15000)


@pytest.mark.regression
def test_login_button_disabled_when_empty(page: Page):
    page.goto("https://panorra.com/", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    expect(page).to_have_title(re.compile("Panorra"), timeout=60000)

    page.get_by_role("link", name="Log In").click()
    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_disabled()


@pytest.mark.unit
def test_login_page_ui_elements(page: Page):
    page.goto("https://panorra.com/", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=70000)

    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=60000)
    login_link.click()

    email_field = page.get_by_placeholder("Enter your email or username")
    password_field = page.get_by_placeholder("Enter your password")
    expect(email_field).to_be_visible(timeout=60000)
    expect(password_field).to_be_visible(timeout=60000)

    expect(page.get_by_text("Password", exact=True)).to_be_visible(timeout=60000)
    expect(page.get_by_text("Email/Username", exact=True)).to_be_visible(timeout=60000)
    expect(page.get_by_role("heading", name="Log In to Panorra")).to_be_visible(timeout=60000)

    expect(page.locator("div").filter(has_text="Log In to Panorra").first).to_be_visible(timeout=60000)

    expect(page.get_by_text("Forgot your password?")).to_be_visible(timeout=60000)
    expect(page.get_by_text("OR", exact=True)).to_be_visible(timeout=60000)
    expect(page.get_by_text("Need a Panorra account?")).to_be_visible(timeout=60000)

    google_iframe = page.frame_locator('iframe[title*="Google"]')
    expect(google_iframe.get_by_role("button")).to_be_visible(timeout=60000)
