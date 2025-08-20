import pytest
import os
import re
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
    
    page.get_by_role("button", name="header menu").click()
    page.locator('a:has-text("Log Out")').click()

    # Verify logout was successful
    expect(page.get_by_role("link", name="Log In")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_hidden(timeout=SHORT_TIMEOUT)
    
    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_opening_menu_does_not_logout(page: Page, base_url, username, password):
    """Verifies that just opening the menu does not log the user out."""
    login_user(page, base_url, username, password)
    page.get_by_role("button", name="header menu").click()
    
    # Verify the menu appears and the user remains logged in
    expect(page.locator('a:has-text("Log Out")')).to_be_visible(timeout=SHORT_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible()
    
    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)


@pytest.mark.unit
def test_logout_button_functionality(page: Page, base_url, username, password, take_screenshot):
    """Verifies the functionality of the logout button and takes screenshots."""
    # --- THIS TEST IS UNCHANGED AS PER YOUR REQUEST ---
    login_user(page, base_url, username, password)
    take_screenshot("login_successful")
    
    page.get_by_role("button", name="header menu").click()
    take_screenshot("header_menu_visible")
    
    logout_link = page.locator('a:has-text("Log Out")')
    expect(logout_link).to_be_visible(timeout=SHORT_TIMEOUT)
    logout_link.click()
    
    expect(page.get_by_role("link", name="Log In")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_hidden(timeout=SHORT_TIMEOUT)
    take_screenshot("logout_successful")

@pytest.mark.regression
def test_session_persists_after_browser_close(browser: BrowserContext, page: Page, base_url, username, password):
    """Verifies that the login session persists after the browser is closed and reopened."""
    # --- THIS TEST IS UNCHANGED BECAUSE IT CLOSES THE PAGE MANUALLY ---
    storage_state_path = "state.json"
    
    login_user(page, base_url, username, password)
    page.context.storage_state(path=storage_state_path)
    page.context.close()
    
    # Open a new context with the saved state
    new_context = browser.new_context(storage_state=storage_state_path)
    new_page = new_context.new_page()
    new_page.goto(base_url, timeout=LONG_TIMEOUT)

    # Verify that the user is still logged in
    expect(new_page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(new_page.get_by_role("link", name="Log In")).to_be_hidden(timeout=SHORT_TIMEOUT)
    
    new_context.close()
    if os.path.exists(storage_state_path):
        os.remove(storage_state_path)