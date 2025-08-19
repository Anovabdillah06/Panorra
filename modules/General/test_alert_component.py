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
    print("Navigating to login page...")
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    login_link = page.get_by_role("link", name="Log In")
    expect(login_link).to_be_visible(timeout=MEDIUM_TIMEOUT)
    login_link.click()
    
    page.get_by_placeholder("Enter your email or username").fill(username)
    page.get_by_placeholder("Enter your password").fill(password)
    page.get_by_role("button", name="Log In").click(timeout=LONG_TIMEOUT)
    
    # Verify login was successful
    dashboard_heading = page.get_by_role("heading", name="Recommendation for You")
    expect(dashboard_heading).to_be_visible(timeout=LONG_TIMEOUT)
    print("Login successful.")

# =====================================================================
# Final Test Suite
# =====================================================================

@pytest.mark.smoke
def test_success_and_error_alerts_flow(page: Page, base_url, username, password):
    """
    Verifies the success alert flow (block post) and the error alert flow (invalid profile edit)
    in a single smoke test.
    """
    # 1. Login to the application
    login_user(page, base_url, username, password)
    
    # --- PART 1: VERIFY SUCCESS ALERT ---
    print("\n--- Testing Success Alert: Blocking a Post ---")
    
    # 2. Click the first post on the main page
    print("Opening the first post...")
    page.locator('.d-block.w-100').first.click()
    
    # 3. Open the options menu and block the post
    print("Blocking the post...")
    page.locator('.flex-align-center > app-detail-menu > .header-more > #dropdownBasic1').click()
    page.get_by_role('link', name='Block Post').click()
    page.get_by_role('button', name='Confirm').click()
    
    # 4. Verify the success alert appears
    print("Verifying success alert...")
    success_alert = page.get_by_text('Success Block Post')
    expect(success_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Success alert for blocking post verified.")

    # --- PART 2: VERIFY ERROR ALERT ---
    print("\n--- Testing Error Alert: Invalid Profile Edit ---")

    # 5. Navigate to the Edit Profile page
    print("Navigating to Edit Profile page...")
    page.get_by_role('button', name='header menu').click()
    page.get_by_text('Profile').click()
    page.get_by_role('button', name='Edit Profile').click()
    
    # 6. Enter an overly long (invalid) name
    print("Entering an invalid full name...")
    invalid_name = "Arnov Abdillah Rahman Paasdjahjskdakjsdbalsbd njang Banget Nama Nya"
    full_name_input = page.get_by_role('textbox', name='Enter full name')
    full_name_input.fill(invalid_name)
    
    # 7. Try to save the profile
    page.get_by_role('button', name='Save Profile').click()
    
    # 8. Verify the error alert appears
    print("Verifying error alert...")
    error_alert = page.get_by_text('Not valid fullname, fullname')
    expect(error_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Error alert for invalid full name verified.")

@pytest.mark.regression
def test_cancel_block_post_action(page: Page, base_url, username, password):
    """
    Verifies that the user can cancel the "Block Post" action
    from the confirmation dialog.
    """
    # 1. Login to the application
    login_user(page, base_url, username, password)
    
    # 2. Click the first post to open it
    print("Opening the first post...")
    page.locator('.d-block.w-100').first.click()
    
    # 3. Open the options menu
    print("Opening post options menu...")
    menu_button = page.get_by_role("button", name="button menu")
    menu_button.click()
    
    # 4. Click the "Block Post" link
    print("Clicking 'Block Post'...")
    page.get_by_role('link', name='Block Post').click()
    
    # 5. Verify the confirmation dialog appears (by finding the "Cancel" button)
    cancel_button = page.get_by_role('button', name='Cancel')
    expect(cancel_button).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # 6. Click the "Cancel" button to abort the action
    print("Canceling the action...")
    cancel_button.click()
    
    # 7. Verify that the confirmation dialog has closed
    #    and the user is back to the previous state (options menu is still visible)
    print("Verifying the action was cancelled...")
    expect(cancel_button).to_be_hidden(timeout=MEDIUM_TIMEOUT)
    print("Block post action was successfully cancelled.")   

@pytest.mark.regression
def test_alert_does_not_appear_spontaneously(page: Page, base_url,username , password):
    """
    Verifies that an alert does not appear without a user trigger.
    """
    login_user(page, base_url, username, password)
    
    generic_alert = page.locator('[role="alert"]')
    expect(generic_alert).to_be_hidden()
    print("Test passed. No spontaneous alert was found.")

@pytest.mark.regression
def test_no_action_on_confirmation_dialog(page: Page, base_url, username, password):
    """
    Verifies that the system waits and no alert appears
    if the user does nothing on the "Block Post" confirmation dialog.
    """
    # 1. Login and navigate to trigger an action
    login_user(page, base_url, username, password)
    page.locator('.d-block.w-100').first.click() # Click post
    
    # 2. Open the menu and click "Block Post" to show the confirmation dialog
    page.locator('.flex-align-center > app-detail-menu > .header-more > #dropdownBasic1').click()
    page.get_by_role('link', name='Block Post').click()
    
    # 3. Ensure the confirmation dialog (conditional page) has appeared
    print("Confirmation dialog is visible...")
    confirm_button = page.get_by_role('button', name='Confirm')
    expect(confirm_button).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # 4. User DOES NOTHING. We simulate this by waiting.
    print("User does nothing for 3 seconds...")
    page.wait_for_timeout(3000)
    
    # 5. Verify that the page state has not changed
    #    - The confirmation dialog should still be visible.
    #    - The success alert ("Success Block Post") should NOT appear.
    print("Verifying that the state has not changed...")
    
    # Assertion 1: Ensure the dialog is still present
    expect(confirm_button).to_be_visible()
    
    # Assertion 2: Ensure the success alert did not appear
    success_alert = page.get_by_text('Success Block Post')
    expect(success_alert).to_be_hidden()
    
    print("Test passed. System correctly waited for user input.")

@pytest.mark.unit
def test_login_ui_and_alerts_flow(page: Page, base_url, username, password, take_screenshot):
    """
    Complete smoke test:
    1. Login.
    2. Check UI components.
    3. Verify success alert.
    4. Verify error alert.
    """
    # 1. LOGIN
    login_user(page, base_url, username, password)
    
    # 2. CHECK UI COMPONENTS AFTER LOGIN
    print("\n--- Verifying Dashboard UI Components ---")
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible()
    expect(page.get_by_role("button", name="header menu")).to_be_visible()
    expect(page.get_by_role("link", name="banner")).to_be_visible()
    print("Dashboard UI components are visible.")
    take_screenshot("login_success")

    # 3. VERIFY SUCCESS ALERT (BLOCK POST)
    print("\n--- Testing Success Alert: Blocking a Post ---")
    page.locator('.d-block.w-100').first.click()
    print("Opening the first post...")
    
    page.locator('.flex-align-center > app-detail-menu > .header-more > #dropdownBasic1').click()
    page.get_by_role('link', name='Block Post').click()
    page.get_by_role('button', name='Confirm').click()
    print("Post blocked.")
    
    success_alert = page.get_by_text('Success Block Post')
    expect(success_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Success alert verified.")
    take_screenshot("Session_success_alert")

    # 4. VERIFY ERROR ALERT (EDIT PROFILE)
    print("\n--- Testing Error Alert: Invalid Profile Edit ---")
    page.get_by_role('button', name='header menu').click()
    page.get_by_text('Profile').click()
    page.get_by_role('button', name='Edit Profile').click()
    print("Navigated to Edit Profile page.")
    
    invalid_name = "This Name Is Clearly Too Long To Be Saved in the Database and Should Be Rejected By The Validation System"
    page.get_by_role('textbox', name='Enter full name').fill(invalid_name)
    page.get_by_role('button', name='Save Profile').click()
    print("Attempting to save with invalid name...")
    
    error_alert = page.get_by_text('Not valid fullname, fullname')
    expect(error_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Error alert verified.")
    take_screenshot("Session_error_alert")
    
    print("\nFull unit test completed successfully.")