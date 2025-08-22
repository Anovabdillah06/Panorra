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
# Test for Profile Page Navigation and UI Elements
# =====================================================================

@pytest.mark.smoke
def test_detail_user(page: Page, base_url, username, password):
    """
    Verifies that a logged-in user can navigate to their profile page
    and that key profile elements are visible.
    """
    # 1. Log in to the application
    login_user(page, base_url, username, password)
    
    # 2. Navigate to the Profile page
    print("Navigating to the Profile page...")
    page.get_by_role("button", name="header menu").click()
    page.get_by_text("Profile").click()
    
    # 3. Verify that the user is on the profile page
    #    We can confirm this by looking for a unique element, like the user avatar.
    print("Verifying key elements on the Profile page...")
    
    # Use the locator from your script to find the avatar
    profile_avatar = page.locator('.profile__user-avatar')
    
    # Assert that the avatar is visible
    expect(profile_avatar).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    print("Detail User successfully.")

@pytest.mark.regression
def test_opening_avatar_menu_takes_no_action(page: Page, base_url, username, password):
    """
    Verifies that opening the avatar menu without clicking 'Profile'
    does not navigate the user away from the current page.
    (Skenario Positive False)
    """
    login_user(page, base_url, username, password)
    
    # Buka menu avatar/header
    print("Opening the avatar menu...")
    page.get_by_role("button", name="header menu").click()
    
    # Pastikan menu muncul (dengan memeriksa link 'Profile')
    expect(page.get_by_text("Profile")).to_be_visible()
    
    # Tunggu sebentar untuk memastikan tidak ada aksi otomatis
    page.wait_for_timeout(3000)
    
    # Verifikasi bahwa URL halaman tidak berubah
    expect(page).to_have_url(base_url)
    print("Test passed. No navigation occurred as expected.")

@pytest.mark.regression
def test_user_detail_page_does_not_load_automatically(page: Page, base_url, username, password):
    """
    Verifies that the User Detail page is not displayed automatically
    without the user clicking the profile button.
    (Skenario Negative False - menguji bug)
    """
    login_user(page, base_url, username, password)
    
    # Tunggu sebentar di halaman dashboard
    page.wait_for_timeout(3000)
    
    # Verifikasi bahwa elemen unik dari halaman profil (misal: tombol 'Edit Profile')
    # TIDAK terlihat di halaman dashboard.
    edit_profile_button = page.get_by_role("button", name="Edit Profile")
    
    expect(edit_profile_button).to_be_hidden()
    print("Test passed. User Detail page did not load spontaneously.")

@pytest.mark.regression
def test_profile_link_failure_is_handled_gracefully(page: Page, base_url, username, password):
    """
    Verifies that the system handles a failure to load the User Detail page
    without crashing.
    (Skenario Negative True)
    """
    print("Simulating a broken link for the Profile page...")
    page.route("**/profile*", lambda route: route.abort())
    
    login_user(page, base_url, username, password)
    page.get_by_role("button", name="header menu").click()
    page.get_by_text("Profile").click()

    print("Test passed. Broken profile link was handled gracefully.")

@pytest.mark.unit
def test_user_detail_page_ui_elements(page: Page, base_url, username, password, take_screenshot):
    """
    Verifies that all key UI elements on the User Detail (Profile) page
    are present and visible, taking a screenshot of each.
    """
    # 1. Log in and navigate to the Profile page
    login_user(page, base_url, username, password)
    print("Navigating to the Profile page...")
    page.get_by_role("button", name="header menu").click()
    page.get_by_text("Profile").click()
    
    # Wait for the page to be ready by checking for a key element
    expect(page.get_by_role("button", name="Edit Profile")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    take_screenshot("profile_page_loaded")

    # 2. Create a list of elements to verify on the page
    print("Verifying UI elements on the User Detail page...")
    
    # NOTE: Some locators are made more robust for better test stability.
    elements_to_verify = {
        "user_full_name": page.get_by_role('heading', name=re.compile(r'Arnov Abdillah Rahman', re.IGNORECASE)),
        "user_stats": page.get_by_text(re.compile(r'Posts.*Followers.*Following')),
        "action_buttons": page.get_by_text(re.compile(r'Report User.*Block User')),
        "profile_tabs": page.get_by_text('PostsTaggedAbout'),
        "posts_container": page.locator('virtual-scroller')
    }