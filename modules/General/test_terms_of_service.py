import pytest
import re
from playwright.sync_api import Page, expect

# =====================================================================
# Constants for Timeout
# =====================================================================
LONG_TIMEOUT = 60000      # Timeout for page navigation
MEDIUM_TIMEOUT = 15000    # Timeout for element verification

# =====================================================================
# Test for Terms of Service Link
# =====================================================================

@pytest.mark.smoke
def test_terms_of_service_link_opens_correctly(page: Page, base_url):
    """
    Verifies that the 'Terms of Service' link is found after scrolling
    and opens the correct page in a new tab.
    """
    # 1. Navigate to the homepage
    page.goto(base_url, timeout=LONG_TIMEOUT)

    # 2. Verify that the left navigation panel is visible first.
    #    This confirms the main page UI has loaded correctly.
    print("Verifying that the left navigation panel is visible...")
    left_nav_panel = page.locator("div", has_text=re.compile(r'RecentJust for YouNearest')).nth(2)
    expect(left_nav_panel).to_be_visible(timeout=MEDIUM_TIMEOUT)

    # 3. Directly locate the 'Terms of Service' link on the page.
    terms_link = page.get_by_role("link", name="Terms of Service")
    
    # 4. Scroll the page until that specific link is visible.
    print("Scrolling to find the Terms of Service link...")
    terms_link.scroll_into_view_if_needed(timeout=MEDIUM_TIMEOUT)
    expect(terms_link).to_be_visible()
    
    # 5. Wait for the new tab to open after clicking.
    with page.context.expect_event("page") as new_page_info:
        terms_link.click()
    
    terms_page = new_page_info.value
    
    # 6. Verify the content on the new Terms of Service page.
    print("Verifying content on the new Terms of Service page...")
    terms_page.wait_for_load_state(timeout=LONG_TIMEOUT)
    
    # Assert that the main heading is visible.
    heading = terms_page.get_by_role('heading', name='TERMS OF USE')
    expect(heading).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # Assert that a key part of the text is present.
    intro_text = terms_page.get_by_text('BY CLICKING "I AGREE" OR')
    expect(intro_text).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    print("Terms of Service page verified successfully.")
    terms_page.close()

    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_no_click_on_tos_link_takes_no_action(page: Page, base_url):
    """
    Verifies that the system takes no action if the user does not click
    the 'Terms of Service' link.
    (Positive False Scenario)
    """
    # 1. Open the main page
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 2. Ensure the Terms of Service link exists (but don't click it)
    tos_link = page.get_by_role("link", name="Terms of Service")
    tos_link.scroll_into_view_if_needed(timeout=MEDIUM_TIMEOUT)
    expect(tos_link).to_be_visible()
    
    # 3. Wait a moment to ensure no automatic action occurs
    page.wait_for_timeout(3000)
    
    # 4. Verify that the page URL remains the same (no redirect)
    expect(page).to_have_url(base_url)
    print("Test passed. No action was taken as expected.")
    
    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_tos_page_does_not_load_automatically(page: Page, base_url):
    """
    Verifies that the Terms of Service page does not load automatically
    without any user interaction.
    (Negative False Scenario - testing for a bug)
    """
    # 1. Open the main page
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 2. Wait a moment
    page.wait_for_timeout(3000)
    
    # 3. Verify that content from the ToS page (e.g., the heading) is NOT visible
    tos_heading = page.get_by_role('heading', name='TERMS OF USE')
    
    # This test will pass if the heading is NOT found.
    expect(tos_heading).to_be_hidden()
    print("Test passed. ToS page did not load spontaneously.")

    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_broken_tos_link_is_handled_gracefully(page: Page, base_url):
    """
    Verifies that the system handles a broken 'Terms of Service' link
    gracefully without crashing.
    (Negative True Scenario)
    """
    # 1. Simulate that the ToS link is broken by intercepting the navigation
    #    Replace '**/terms-of-service' with the actual ToS page URL.
    print("Simulating a broken link for the Terms of Service page...")
    page.route("**/terms-of-service", lambda route: route.abort())
    
    # 2. Open the main page
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 3. Find and click the Terms of Service link
    tos_link = page.get_by_role("link", name="Terms of Service")
    tos_link.scroll_into_view_if_needed()
    expect(tos_link).to_be_visible()
    tos_link.click()
    
    # 4. Verify that the user remains on the current page (no change)
    #    or is directed to a proper error page, but does not crash.
    #    Here we ensure the URL does not change.
    print("Verifying the user remains on the current page...")
    expect(page).to_have_url(base_url)
    print("Test passed. Broken link was handled gracefully.")
    
    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)

@pytest.mark.unit
def test_terms_of_service_page_ui_elements_with_scroll(page: Page, base_url, take_screenshot):
    """
    Verifies key UI elements on the Terms of Service page by scrolling
    to each element and checking its visibility. A single manual full-page screenshot
    is taken at the end.
    """
    # 1. Navigate to the homepage and click the Terms of Service link
    page.goto(base_url, timeout=LONG_TIMEOUT)
    print("Opening the Terms of Service page...")
    tos_link = page.get_by_role("link", name="Terms of Service")
    tos_link.scroll_into_view_if_needed(timeout=MEDIUM_TIMEOUT)
    
    with page.context.expect_event("page") as new_page_info:
        tos_link.click()
    
    terms_page = new_page_info.value
    terms_page.wait_for_load_state(timeout=LONG_TIMEOUT)

    # 2. Verify each element by scrolling to it first
    print("Verifying each element on the ToS page with a scroll...")

    # A list of elements to check on the page
    elements_to_check = [
        terms_page.get_by_role('heading', name='TERMS OF USE'),
        terms_page.get_by_text('Effective Date: 28th April'),
        terms_page.get_by_text('BY CLICKING "I AGREE" OR'),
        terms_page.get_by_text('1. UPDATES'),
        terms_page.get_by_text('2. SCOPE OF SERVICE; ACCESS TO THE SERVICE'),
        terms_page.get_by_text('3. ADVERTISEMENTS'),
        terms_page.get_by_text('4. USE OF THE SERVICE'),
        terms_page.get_by_text('5. TERMINATION'),
        terms_page.get_by_text('6. OWNERSHIP RIGHTS'),
        terms_page.get_by_text('DISCLAIMER, LIMITATION OF LIABILITY AND INDEMNITY'),
        terms_page.get_by_text('8. GENERAL')
    ]
    take_screenshot("Terms_of_service_elements")
    # Loop to scroll and verify each element
    for element in elements_to_check:
        element.scroll_into_view_if_needed(timeout=MEDIUM_TIMEOUT)
        expect(element).to_be_visible()
        element_text = element.inner_text().split('\n')[0]
        print(f"  - Verified: '{element_text[:30]}...' is visible.")
    
    # 3. Take ONE manual full-page screenshot after all verifications are successful
    print("\nAll sections verified. Taking a final full-page screenshot...")

    terms_page.close()