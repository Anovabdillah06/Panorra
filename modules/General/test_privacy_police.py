import pytest
import re
from playwright.sync_api import Page, expect

# =====================================================================
# Constants for Timeout
# =====================================================================
LONG_TIMEOUT = 60000      # Timeout for page navigation
MEDIUM_TIMEOUT = 15000    # Timeout for element verification

# =====================================================================
# Test Suite for Privacy Policy Feature
# =====================================================================

@pytest.mark.smoke
def test_privacy_policy_link_opens_correctly(page: Page, base_url):
    """
    Verifies that the 'Privacy Policy' link is found after scrolling
    and opens the correct page in a new tab.
    """
    # 1. Navigate to the homepage
    page.goto(base_url, timeout=LONG_TIMEOUT)

    # 2. Verify that the left navigation panel is visible first.
    print("Verifying that the left navigation panel is visible...")
    left_nav_panel = page.locator("div", has_text=re.compile(r'RecentJust for YouNearest')).nth(2)
    expect(left_nav_panel).to_be_visible(timeout=MEDIUM_TIMEOUT)

    # 3. Directly locate the 'Privacy Policy' link and scroll to it.
    print("Scrolling to find the Privacy Policy link...")
    privacy_link = page.get_by_role("link", name="Privacy Policy")
    privacy_link.scroll_into_view_if_needed(timeout=MEDIUM_TIMEOUT)
    expect(privacy_link).to_be_visible()
    
    # 4. Wait for the new tab to open after clicking.
    with page.context.expect_event("page") as new_page_info:
        privacy_link.click()
    
    privacy_page = new_page_info.value
    
    # 5. Verify the content on the new Privacy Policy page.
    print("Verifying content on the new Privacy Policy page...")
    privacy_page.wait_for_load_state(timeout=LONG_TIMEOUT)
    
    # Assert that the main heading is visible.
    heading = privacy_page.get_by_role('heading', name='PRIVACY POLICY')
    expect(heading).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    print("Privacy Policy page verified successfully.")
    privacy_page.close()

    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_no_click_on_pp_link_takes_no_action(page: Page, base_url):
    """
    Verifies that the system takes no action if the user does not click
    the 'Privacy Policy' link.
    """
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    privacy_link = page.get_by_role("link", name="Privacy Policy")
    privacy_link.scroll_into_view_if_needed(timeout=MEDIUM_TIMEOUT)
    expect(privacy_link).to_be_visible()
    
    page.wait_for_timeout(3000)
    
    expect(page).to_have_url(base_url)
    print("Test passed. No action was taken as expected.")

    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)

@pytest.mark.regression
def test_broken_pp_link_is_handled_gracefully(page: Page, base_url):
    """
    Verifies that the system handles a broken 'Privacy Policy' link gracefully.
    """
    print("Simulating a broken link for the Privacy Policy page...")
    page.route("**/privacy-policy", lambda route: route.abort())
    
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    privacy_link = page.get_by_role("link", name="Privacy Policy")
    privacy_link.scroll_into_view_if_needed()
    expect(privacy_link).to_be_visible()
    privacy_link.click()
    
    print("Verifying the user remains on the current page...")
    expect(page).to_have_url(base_url)
    print("Test passed. Broken link was handled gracefully.")

    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)

@pytest.mark.unit
def test_privacy_policy_page_all_sections_are_visible(page: Page, base_url, take_screenshot):
    """
    Verifies that all key sections on the Privacy Policy page are visible.
    A single manual full-page screenshot is taken at the end for documentation.
    """
    # 1. Navigate to the homepage and open the Privacy Policy page
    page.goto(base_url, timeout=LONG_TIMEOUT)
    print("Opening the Privacy Policy page...")
    privacy_link = page.get_by_role("link", name="Privacy Policy")
    privacy_link.scroll_into_view_if_needed(timeout=MEDIUM_TIMEOUT)
    
    with page.context.expect_event("page") as new_page_info:
        privacy_link.click()
    
    privacy_page = new_page_info.value
    privacy_page.wait_for_load_state(timeout=LONG_TIMEOUT)

    # 2. Create a list of all elements to be verified on the page
    print("Verifying each section on the Privacy Policy page with a scroll...")

    elements_to_check = [
        privacy_page.get_by_role('heading', name='PRIVACY POLICY'),
        privacy_page.get_by_text('How we obtain your data'),
        privacy_page.get_by_text('2. Personal data we Collect'),
        privacy_page.get_by_text('3. Processing of Your'),
        privacy_page.get_by_text('THIRD-PARTY SERVICES'),
        privacy_page.get_by_text('5. Cookies and DIGITAL'),
        privacy_page.get_by_text('6. Obtaining, rectifying and'),
        privacy_page.get_by_text('7. Data Storage, Retention'),
        privacy_page.get_by_text('8. Children', exact=True),
        privacy_page.get_by_text('DO NOT TRACK DISCLOSURE'),
        privacy_page.get_by_text('10. CALIFORNIA "SHINE THE'),
        privacy_page.get_by_text('YOUR CALIFORNIA PRIVACY RIGHTS'),
        privacy_page.get_by_text('12. European users and rights'),
        privacy_page.get_by_text('13. Change of Ownership or'),
        privacy_page.get_by_text('14. Security'),
        privacy_page.get_by_text('CONTACT PREFERENCES'),
        privacy_page.get_by_text('16. Updates')
    ]

    # 3. Loop through and verify each element is visible (this is fast)
    for element in elements_to_check:
        element.scroll_into_view_if_needed(timeout=MEDIUM_TIMEOUT)
        expect(element).to_be_visible()
        element_text = element.inner_text().split('\n')[0]
        print(f"  - Verified: '{element_text[:40]}...' is visible.")

    # 4. Take ONE manual full-page screenshot after all verifications are successful
    print("\nAll sections verified. Taking a final full-page screenshot...")
    take_screenshot("Privacy_Policy_Elements")
    
    privacy_page.close()