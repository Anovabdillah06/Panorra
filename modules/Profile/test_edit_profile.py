import pytest
import re
import time
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
# Smoke Test for Edit Profile Feature
# =====================================================================

@pytest.mark.smoke
def test_edit_profile_successfully(page: Page, base_url, username, password):
    """
    Smoke test to verify that a user can successfully edit their profile
    information and the changes are saved.
    """
    # 1. Log in to the application
    login_user(page, base_url, username, password)
    
    # 2. Navigate to the Edit Profile page
    print("Navigating to the Edit Profile page...")
    page.get_by_role("button", name="header menu").click()
    page.get_by_text("Profile").click()
    page.get_by_role("button", name="Edit Profile").click()
    
    # Wait for the edit page to be ready
    full_name_input = page.get_by_role('textbox', name='Enter full name')
    expect(full_name_input).to_be_visible(timeout=MEDIUM_TIMEOUT)

    # 3. Define new profile information and fill the form
    #    Using a timestamp to ensure the name is unique for each test run
    new_full_name = f"Arnov Abdillah Rahman"
    new_description = f"Testing."
    
    print(f"Updating profile name to: '{new_full_name}'")
    full_name_input.fill(new_full_name)
    
    print(f"Updating description...")
    page.get_by_role('textbox', name='Enter description about me').fill(new_description)
    
    # 4. Save the profile and verify the success alert
    print("Saving profile changes...")
    page.get_by_role("button", name="Save Profile").click()
    
    success_alert = page.get_by_text("Success update profile")
    expect(success_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Success alert verified.")
    
    # 5. Re-navigate to the profile page to ensure changes are persistent
    print("Re-navigating to profile to verify persistent changes...")
    page.get_by_role("button", name="header menu").click()
    page.get_by_text("Profile", exact=True).click()
    
    # 6. Verify that the new full name is displayed on the profile page
    updated_name_heading = page.get_by_role('heading', name=new_full_name)
    expect(updated_name_heading).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    print("Edit Profile smoke test passed successfully.")

@pytest.mark.regression
def test_notifies_user_with_error_for_invalid_fullname_format(page: Page, base_url, username, password):
    """
    Verifies the system shows an error alert for a full name with invalid characters.
    """
    login_user(page, base_url, username, password)
    print("Navigating to the Edit Profile page...")
    page.get_by_role("button", name="header menu").click()
    page.get_by_text("Profile").click()
    page.get_by_role("button", name="Edit Profile").click()
    
    full_name_input = page.get_by_role('textbox', name='Enter full name')
    expect(full_name_input).to_be_visible(timeout=MEDIUM_TIMEOUT)

    invalid_full_name = "Arnov123!@#"
    print(f"Entering invalid full name: '{invalid_full_name}'")
    full_name_input.fill(invalid_full_name)
    
    page.get_by_role("button", name="Save Profile").click()
    
    print("Verifying that the correct error alert is displayed...")
    # --- MENGGUNAKAN LOCATOR BARU ANDA ---
    error_alert = page.locator("div", has_text="Not valid fullname, fullname").nth(2)
    expect(error_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Test passed. Correct error alert was shown for invalid full name.")

@pytest.mark.regression
def test_prevents_save_for_invalid_fullname(page: Page, base_url, username, password):
    """
    Verifies the system prevents saving and does not show a success alert
    when the full name format is incorrect.
    """
    login_user(page, base_url, username, password)
    page.get_by_role("button", name="header menu").click()
    page.get_by_text("Profile").click()
    page.get_by_role("button", name="Edit Profile").click()
    
    full_name_input = page.get_by_role('textbox', name='Enter full name')
    expect(full_name_input).to_be_visible(timeout=MEDIUM_TIMEOUT)

    invalid_full_name = "This Name Is Way Too Long And Should Be Rejectedddddddd"
    full_name_input.fill(invalid_full_name)
    
    page.get_by_role("button", name="Save Profile").click()
    
    print("Verifying that the success alert is NOT displayed...")
    success_alert = page.get_by_text("Success update profile")
    expect(success_alert).to_be_hidden()
    
    print("Verifying that the user remains on the edit page...")
    expect(page.get_by_role("button", name="Save Profile")).to_be_visible()
    
    print("Test passed. Save was correctly prevented for invalid full name.")

@pytest.mark.regression
def test_displays_error_alert_for_invalid_fullname(page: Page, base_url, username, password):
    """
    Verifies the system displays the error alert for an incorrect full name format.
    """
    login_user(page, base_url, username, password)
    page.get_by_role("button", name="header menu").click()
    page.get_by_text("Profile").click()
    page.get_by_role("button", name="Edit Profile").click()
    
    full_name_input = page.get_by_role('textbox', name='Enter full name')
    expect(full_name_input).to_be_visible(timeout=MEDIUM_TIMEOUT)

    invalid_full_name = "Another Invalid Name 123"
    full_name_input.fill(invalid_full_name)
    
    page.get_by_role("button", name="Save Profile").click()
    
    print("Verifying that the error alert is displayed...")
    # --- MENGGUNAKAN LOCATOR BARU ANDA ---
    error_alert = page.locator("div", has_text="Not valid fullname, fullname").nth(2)
    expect(error_alert).to_be_visible(timeout=MEDIUM_TIMEOUT)
    print("Test passed. Error alert for invalid full name was displayed.")

@pytest.mark.unit
def test_edit_profile_page_ui_elements(page: Page, base_url, username, password, take_screenshot):
    """
    Verifies that all key UI elements on the Edit Profile page are visible
    by scrolling to each one and taking a screenshot.
    """
    # 1. Log in and navigate to the Edit Profile page
    login_user(page, base_url, username, password)
    print("Navigating to the Edit Profile page...")
    page.get_by_role("button", name="header menu").click()
    page.get_by_text("Profile").click()
    page.get_by_role("button", name="Edit Profile").click()
    
    # Wait for the page to be ready by checking for a key element
    expect(page.locator('.edit-profile__avatar')).to_be_visible(timeout=MEDIUM_TIMEOUT)
    take_screenshot("edit_profile_page_loaded")

    # 2. Create a dictionary of all elements to verify
    print("Verifying UI elements on the Edit Profile page...")
    
    elements_to_verify = {
        "avatar_section": page.locator('.edit-profile__avatar'),
        "email_field_label": page.get_by_text("Email*", exact=True),
        "full_name_field_label": page.get_by_text("Full Name*", exact=True),
        "username_field_label": page.get_by_text("Username*", exact=True),
        "birthday_field_label": page.get_by_text("Birthday"),
        "gender_field_label": page.get_by_text("Gender"),
        "country_field_label": page.get_by_text("Country", exact=True),
        "contact_info_heading": page.get_by_text("Contact Info"),
        "about_me_section": page.get_by_text("About Me"),
        "save_profile_button": page.get_by_role("button", name="Save Profile")
    }

    # 3. Loop through the dictionary, scroll, verify, and take a screenshot
    for name, locator in elements_to_verify.items():
        print(f"  - Verifying element: {name}...")
        
        # Scroll to the element to ensure it's in the viewport
        locator.scroll_into_view_if_needed(timeout=MEDIUM_TIMEOUT)
        
        # Verify that the element is visible
        expect(locator).to_be_visible()
        
        # Take a screenshot using the element's name
        take_screenshot(name)
        
        print(f"  - Element '{name}' is visible. Screenshot saved.")
        
    print("\nUI Element Test for Edit Profile page passed successfully.")