import re
import pytest
from playwright.sync_api import Page, expect
from pathlib import Path

# -------------------------------
# Helper
# -------------------------------
def fill_input(page: Page, placeholder: str, value: str):
    """Helper function to fill a form input."""
    field = page.get_by_placeholder(placeholder)
    # .fill() automatically clears the field, so a preceding .fill("") is not needed.
    field.fill(value)
    return field

# -------------------------------
# Test login
# -------------------------------
@pytest.mark.smoke
def test_login_success(page: Page, base_url, username, password):
    """Verifies a successful login."""
    # --- ADDED DEBUGGING STEPS ---
    # Check the page response to ensure there are no access errors (like 403 Forbidden)
    print("Navigating to base_url...")
    response = page.goto(base_url, timeout=30000)
    assert response.status < 400, f"Failed to load the main page. Status: {response.status}"
    print(f"Main page loaded successfully with status: {response.status}")

    page.wait_for_load_state("domcontentloaded", timeout=30000)
    expect(page).to_have_title(re.compile("Panorra"), timeout=15000)

    page.get_by_role("link", name="Log In").click()
    fill_input(page, "Enter your email or username", username)
    fill_input(page, "Enter your password", password)

    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_enabled(timeout=10000)
    login_button.click()

    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception as e:
        print(f"Page did not reach networkidle. Continuing test... Error: {e}")

    heading = page.get_by_role("heading", name="Recommendation for You")
    expect(heading).to_be_visible(timeout=10000)
    assert heading.inner_text().strip() == "Recommendation for You"
    
    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_login_invalid_credentials_password_or_username(page: Page, base_url, username):
    """Verifies the error message for an incorrect password."""
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    page.get_by_role("link", name="Log In").click()
    fill_input(page, "Enter your email or username", username)
    fill_input(page, "Enter your password", "wrong_password_123")

    page.get_by_role("button", name="Log In").click()

    error_message = page.locator("text=Email or Password incorrect")
    expect(error_message).to_be_visible(timeout=10000)
    assert error_message.inner_text().strip() == "Email or Password incorrect"

    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_login_button_disabled_when_empty(page: Page, base_url):
    """Verifies the login button is disabled when the form is empty."""
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    page.get_by_role("link", name="Log In").click()
    login_button = page.get_by_role("button", name="Log In")
    expect(login_button).to_be_disabled(timeout=1000)
    assert not login_button.is_enabled()
    
    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_login_invalid_credentials(page: Page, base_url):
    """Verifies the error message for incorrect username and password."""
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)

    page.get_by_role("link", name="Log In").click()
    fill_input(page, "Enter your email or username", "adawrong")
    fill_input(page, "Enter your password", "wrong_password_123")

    page.get_by_role("button", name="Log In").click()

    error_message = page.locator("text=Email or Password incorrect")
    expect(error_message).to_be_visible(timeout=10000)
    assert error_message.inner_text().strip() == "Email or Password incorrect"

    page.wait_for_timeout(5000)

@pytest.mark.unit
def test_login_page_ui_elements(page: Page, base_url, take_screenshot):
    """Unit test for UI elements on the login page."""
    page.goto(base_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    take_screenshot("homepage_loaded")

    page.get_by_role("link", name="Log In").click()
    
    expect(page.get_by_role("heading", name="Log In to Panorra")).to_be_visible(timeout=10000)
    take_screenshot("login_page_loaded")

    # Verify all elements
    expect(page.get_by_placeholder("Enter your email or username")).to_be_visible()
    expect(page.get_by_placeholder("Enter your password")).to_be_visible()
    expect(page.get_by_text("Password", exact=True)).to_be_visible()
    expect(page.get_by_text("Email/Username", exact=True)).to_be_visible()
    expect(page.get_by_text("Forgot your password?")).to_be_visible()
    expect(page.get_by_text("OR", exact=True)).to_be_visible()
    expect(page.get_by_text("Need a Panorra account?")).to_be_visible()

    
    take_screenshot("all_login_elements_visible")