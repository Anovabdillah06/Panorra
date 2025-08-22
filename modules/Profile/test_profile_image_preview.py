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
    # return ""
    """Centralized function to navigate and perform login."""
    print("Navigating to login page...")
    page.goto(base_url, timeout=LONG_TIMEOUT)
    page.get_by_role("link", name="Log In").click()
    
    print(f"Logging in with username: {username}...")
    page.get_by_role("textbox", name="Enter your email or username").fill(username)
    page.get_by_role("textbox", name="Enter your password").fill(password)
    page.get_by_role("button", name="Log In").click()
    
    # Verify login was successful
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=LONG_TIMEOUT)
    print("Login successful.")

# =====================================================================
# Test for Profile Image Preview Feature
# =====================================================================

@pytest.mark.smoke
def test_profile_image_preview_appears_on_click(page: Page, base_url, username, password):
    # return ""
    """
    Verifies that clicking the user's profile image on their profile page
    successfully opens the image preview dialog.
    """
    # 1. Log in to the application
    login_user(page, base_url, username, password)
    
    # 2. Navigate to the Profile page
    print("Navigating to the Profile page...")
    page.get_by_role("button", name="header menu").click()
    page.get_by_text("Profile").click()
    
    # Wait for the profile page to be ready
    profile_avatar = page.get_by_role('img', name='profile')
    expect(profile_avatar).to_be_visible(timeout=MEDIUM_TIMEOUT)

    # 3. Click the profile image to trigger the preview
    print("Clicking the profile image to open the preview...")
    profile_avatar.click()
    
    # 4. Verify that the image preview dialog appears
    #    We check for the presence of a 'dialog' role, which is common for modals.
    print("Verifying that the image preview dialog is visible...")
    image_preview_dialog = page.get_by_role("dialog")
    
    # Assertion: The dialog should be visible after the click
    expect(image_preview_dialog).to_be_visible(timeout=MEDIUM_TIMEOUT)

    
    print("Profile image preview test passed successfully.")