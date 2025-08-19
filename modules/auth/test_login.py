import re
import pytest
from playwright.sync_api import Page, expect
from pathlib import Path

# -------------------------------
# Helper
# -------------------------------
def fill_input(page: Page, placeholder: str, value: str):
    field = page.get_by_placeholder(placeholder)
    field.fill("")  # Clear first
    field.fill(value)
    # Note: The line below is generally not necessary.
    # Playwright's '.fill()' is very reliable.
    # page.evaluate(f'document.querySelector("[placeholder=\'{placeholder}\']").value = "{value}"')
    return field

# -------------------------------
# Test login
# -------------------------------
@pytest.mark.smoke
def test_login_success(page: Page, base_url, username, password):
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    expect(page).to_have_title(re.compile("Panorra"), timeout=15000)

    page.get_by_role("link", name="Log In").click()
    fill_input(page, "Enter your email or username", username)
    fill_input(page, "Enter your password", password)

    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_enabled(timeout=10000)
    login_button.click()

    # --- SMART WAIT ADDED HERE ---
    # Waiting for the page to finish loading and network activity to settle.
    # This gives the server time to process the login and render the next page.
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception as e:
        print(f"Page did not reach networkidle, possibly due to background activity. Continuing test... Error: {e}")

    # After the wait, we then look for elements on the new page.
    heading = page.get_by_role("heading", name="Recommendation for You")
    expect(heading).to_be_visible(timeout=10000)
    assert heading.inner_text().strip() == "Recommendation for You"


@pytest.mark.regression
def test_login_invalid_credentials_password_or_username(page: Page, base_url, username):
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    page.get_by_role("link", name="Log In").click()
    fill_input(page, "Enter your email or username", username)
    fill_input(page, "Enter your password", "wrong_password_123")

    page.get_by_role("button", name="Log In").click()

    # In this case, 'expect().to_be_visible()' is a sufficient wait
    # because we are not navigating, just waiting for an error message to appear.
    error_message = page.locator("text=Email or Password incorrect")
    expect(error_message).to_be_visible(timeout=10000)
    assert error_message.inner_text().strip() == "Email or Password incorrect"


@pytest.mark.regression
def test_login_button_disabled_when_empty(page: Page, base_url):
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    page.get_by_role("link", name="Log In").click()
    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_disabled(timeout=1000)
    assert not login_button.is_enabled()
 

@pytest.mark.regression
def test_login_invalid_credentials(page: Page, base_url, username):
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    page.get_by_role("link", name="Log In").click()
    fill_input(page, "Enter your email or username", "adawrong")
    fill_input(page, "Enter your password", "wrong_password_123")

    page.get_by_role("button", name="Log In").click()

    # In this case, 'expect().to_be_visible()' is a sufficient wait
    # because we are not navigating, just waiting for an error message to appear.
    error_message = page.locator("text=Email or Password incorrect")
    expect(error_message).to_be_visible(timeout=10000)
    assert error_message.inner_text().strip() == "Email or Password incorrect"

@pytest.mark.unit
def test_login_page_ui_elements(page: Page, base_url, take_screenshot):
    """
    UI unit test with the automatic screenshot feature from conftest.py.
    """
    # --- Test Flow ---
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    take_screenshot("homepage_loaded")

    page.get_by_role("link", name="Log In").click()
    
    # Wait for the heading to appear to ensure the login page is ready
    expect(page.get_by_role("heading", name="Log In to Panorra")).to_be_visible(timeout=10000)
    take_screenshot("login_page_loaded")

    # Verify all elements on the login page
    expect(page.get_by_placeholder("Enter your email or username")).to_be_visible(timeout=10000)
    expect(page.get_by_placeholder("Enter your password")).to_be_visible(timeout=10000)
    expect(page.get_by_text("Password", exact=True)).to_be_visible(timeout=10000)
    expect(page.get_by_text("Email/Username", exact=True)).to_be_visible(timeout=10000)
    expect(page.get_by_text("Forgot your password?")).to_be_visible(timeout=10000)
    expect(page.get_by_text("OR", exact=True)).to_be_visible(timeout=10000)
    expect(page.get_by_text("Need a Panorra account?")).to_be_visible(timeout=10000)

    iframe_locator = page.locator('iframe[title*="Google"]')
    expect(iframe_locator).to_be_visible(timeout=10000)
    
    google_iframe = page.frame_locator('iframe[title*="Google"]')
    expect(google_iframe.get_by_role("button")).to_be_visible(timeout=10000)
    
    # Take the final screenshot as proof that all elements are visible
    take_screenshot("all_login_elements_visible")

    # done