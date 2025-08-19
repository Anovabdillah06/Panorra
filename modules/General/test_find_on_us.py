import pytest
import re
from playwright.sync_api import Page, expect

# =====================================================================
# Constants for Timeout
# =====================================================================
LONG_TIMEOUT = 60000      # Timeout for page navigation and critical actions
MEDIUM_TIMEOUT = 13000    # Timeout for standard element verification

# =====================================================================
# Test using original locators
# =====================================================================

@pytest.mark.smoke
def test_app_store_links_with_original_locators(page: Page, base_url):
    """
    Verifies the app store links using the original locators from the script.
    """
    # 1. Navigate to the homepage
    page.goto(base_url, timeout=LONG_TIMEOUT)

    # --- VERIFY FIRST LINK (GOOGLE PLAY) ---
    print("Verifying the first link (Google Play)...")
    
    # FIX: Remove parentheses from .first
    first_link_locator = page.get_by_role("list").filter(has_text=re.compile(r'^$')).get_by_role("link").first
    expect(first_link_locator).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    with page.context.expect_event("page") as new_page_info:
        first_link_locator.click()
        
    google_play_page = new_page_info.value
    google_play_page.wait_for_load_state(timeout=LONG_TIMEOUT)
    
    # Verify content on the Google Play page
    expect(google_play_page.get_by_text("Panorra", exact=True)).to_be_visible(timeout=MEDIUM_TIMEOUT)
    google_play_page.close()
    print("First link verified successfully.")

    # --- VERIFY SECOND LINK (APPLE APP STORE) ---
    print("\nVerifying the second link (Apple App Store)...")

    # Using the original locator from your script, adapted for Python
    # .nth(1) is correct because it is a method/function
    second_link_locator = page.get_by_role("list").filter(has_text=re.compile(r'^$')).get_by_role("link").nth(1)
    expect(second_link_locator).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    with page.context.expect_event("page") as new_page_info:
        second_link_locator.click()
        
    app_store_page = new_page_info.value
    app_store_page.wait_for_load_state(timeout=LONG_TIMEOUT)
    
    # Verify content on the Apple App Store page
    expect(app_store_page.get_by_role("heading", name="Panorra 4+")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    app_store_page.close()
    print("Second link verified successfully.")
    page.wait_for_timeout(3000)

@pytest.mark.regression
def test_no_click_on_find_us_on_does_not_redirect(page: Page, base_url):
    """
    Verifies that the user is not redirected to the app store if they
    only view the page and do not click the link in the "Find Us On" section.
    (Positive False Scenario)
    """
    # 1. Open the main page
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 2. Verify that the left navigation panel is visible (as requested)
    print("Verifying that the left navigation panel is visible...")
    left_nav_panel = page.locator("div", has_text=re.compile(r'RecentJust for YouNearest')).nth(2)
    expect(left_nav_panel).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # 5. Verify that the page URL remains the same
    expect(page).to_have_url(base_url)
    print("Test passed. No redirect was triggered.")
    page.wait_for_timeout(3000)

@pytest.mark.regression
def test_feature_load_failure_does_not_auto_redirect(page: Page, base_url):
    """
    Verifies that if the "Find Us On" feature fails to load, the system
    does NOT perform an automatic redirect (testing for a bug).
    (Negative False Scenario)
    """
    # 1. Simulate a failed load condition by blocking the API or script
    #    that loads the "Find Us On" feature.
    #    Replace '**/api/find-us-on*' with the actual API path.
    print("Simulating a failure to load the 'Find Us On' feature...")
    page.route("**/api/find-us-on*", lambda route: route.abort())
    
    # 2. Open the main page
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 3. Wait a moment to allow for any automatic redirect
    page.wait_for_timeout(3000)

    # 4. Main verification: Ensure the page URL does NOT change.
    #    This test will pass if there is NO redirect.
    expect(page).to_have_url(base_url)
    print("Test passed. The system correctly did not redirect on feature load failure.")
    page.wait_for_timeout(3000)

@pytest.mark.unit
def test_homepage_elements_are_visible(page: Page, base_url, take_screenshot):
    """
    Verifies that key elements on the homepage are visible, including those
    that require scrolling. This test uses specific locators as requested.
    """
    # 1. Navigate to the homepage
    page.goto(base_url, timeout=LONG_TIMEOUT)

    # 2. Verify elements visible on initial load (Above the Fold)
    print("Verifying elements visible on initial load...")

    # Verify the left navigation panel using your locator
    left_nav_panel = page.locator("div", has_text=re.compile(r'RecentJust for YouNearest')).nth(2)
    expect(left_nav_panel).to_be_visible(timeout=MEDIUM_TIMEOUT)

    # Verify the "Recommendation for You" heading
    recommendation_heading = page.get_by_role("heading", name="Recommendation for You")
    expect(recommendation_heading).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    print("Initial elements are visible.")
    take_screenshot("Session_enter_mainpage")
    
    # 3. Scroll to the bottom of the page to find the footer elements
    print("Scrolling to the bottom of the page...")
    # A simple and effective way to scroll to the very bottom
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    
    # 4. Verify elements visible after scrolling (Below the Fold)
    print("Verifying elements visible after scrolling...")
    
    # Verify the "Find Us On" heading
    find_us_on_heading = page.get_by_role("heading", name="Find Us On")
    expect(find_us_on_heading).to_be_visible(timeout=MEDIUM_TIMEOUT)

    # Verify the first download link (Google Play) using the original locator
    first_download_link = page.get_by_role("list").filter(has_text=re.compile(r'^$')).get_by_role("link").first
    expect(first_download_link).to_be_visible(timeout=MEDIUM_TIMEOUT)
    take_screenshot("google_play_link_visible")
    
    # Verify the second download link (App Store) using the original locator
    second_download_link = page.get_by_role("list").filter(has_text=re.compile(r'^$')).get_by_role("link").nth(1)
    expect(second_download_link).to_be_visible(timeout=MEDIUM_TIMEOUT)
    take_screenshot("App_Store_link_visible")

    print("All key elements have been successfully verified.")