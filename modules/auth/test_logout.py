import pytest
import os
import re  # Added to use regular expressions
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
# Test Suite
# =====================================================================

@pytest.mark.smoke
def test_logout_success(page: Page, base_url, username, password):
    """Verifies that the user can log out successfully."""
    login_user(page, base_url, username, password)
    
    # --- NEW LOGOUT FLOW ---
    page.get_by_role("button", name="header menu").click()
    # Using regex to match "Log Out" and ignore any icons
    page.get_by_role("link", name=re.compile("Log Out")).click()
    # Clicking the logout confirmation button
    page.get_by_role("button", name="Log Out").click()
    # --- END OF NEW LOGOUT FLOW ---

    # Verify logout was successful
    expect(page.get_by_role("link", name="Log In")).to_be_visible(timeout=LONG_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_hidden(timeout=LONG_TIMEOUT)
    
    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_opening_menu_does_not_logout(page: Page, base_url, username, password):
    """Verifies that just opening the menu does not log the user out."""
    login_user(page, base_url, username, password)
    page.get_by_role("button", name="header menu").click()
    
    # Verify the menu appears and the user remains logged in
    # Selector updated for better reliability
    expect(page.get_by_role("link", name=re.compile("Log Out"))).to_be_visible(timeout=LONG_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible()
    
    page.wait_for_timeout(5000)


@pytest.mark.unit
def test_logout_button_functionality(page: Page, base_url, username, password, take_screenshot):
    """Verifies the functionality of the logout button and takes screenshots."""
    login_user(page, base_url, username, password)
    take_screenshot("login_successful")
    
    # --- NEW LOGOUT FLOW ---
    page.get_by_role("button", name="header menu").click()
    take_screenshot("header_menu_visible")
    
    # Click the logout link in the menu
    logout_link = page.get_by_role("link", name=re.compile("Log Out"))
    expect(logout_link).to_be_visible(timeout=LONG_TIMEOUT)
    logout_link.click()

    # Click the logout confirmation button that appears
    logout_confirmation_button = page.get_by_role("button", name="Log Out")
    expect(logout_confirmation_button).to_be_visible(timeout=SHORT_TIMEOUT)
    logout_confirmation_button.click()
    # --- END OF NEW LOGOUT FLOW ---
    
    expect(page.get_by_role("link", name="Log In")).to_be_visible(timeout=LONG_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_hidden(timeout=LONG_TIMEOUT)
    take_screenshot("logout_successful")


@pytest.mark.regression
def test_session_persists_after_browser_close(browser: BrowserContext, page: Page, base_url, username, password):
    """
    Verifies that a login session persists after closing and reopening the browser,
    using a new context with custom HTTP headers.
    """
    storage_state_path = "state.json"
    
    # 1. Log in as usual and save the session state
    login_user(page, base_url, username, password)
    page.context.storage_state(path=storage_state_path)
    page.context.close()
    
    # 2. Prepare arguments for the new browser context.
    #    This will include the saved session state AND custom headers.
    context_args = {
        "storage_state": storage_state_path,
        "extra_http_headers": {
            "Access-Code": os.getenv("ACCESS_CODE", "default-code-if-not-set") 
            # Using os.getenv to retrieve ACCESS_CODE from an environment variable
        }
    }
    
    # Optional: Add logic for video recording based on your needs
    # is_flow_test = False # Replace with your logic to determine this
    # if is_flow_test:
    #     context_args["record_video_dir"] = "/path/to/videos"

    # 3. Create a new context and page using the prepared arguments
    new_context = browser.new_context(**context_args)
    new_page = new_context.new_page()
    new_page.goto(base_url, timeout=LONG_TIMEOUT)

    # 4. Verify that the user is still logged in
    expect(new_page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=LONG_TIMEOUT)
    
    # 5. Perform cleanup as usual
    new_context.close()
    if os.path.exists(storage_state_path):
        os.remove(storage_state_path)