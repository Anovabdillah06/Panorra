import pytest
import re
from playwright.sync_api import Page, expect

# =====================================================================
# Constants for Timeout
# =====================================================================
LONG_TIMEOUT = 30000
MEDIUM_TIMEOUT = 15000

# =====================================================================
# Test Suite for Guest User Lost Connection Scenarios
# =====================================================================

@pytest.mark.smoke
def test_lost_connection_page_appears(page: Page, base_url):
    """
    Verifies the system displays the Lost Connection page when a guest
    tries to navigate while offline.
    (Negative True Scenario)
    """
    try:
        page.goto(base_url, timeout=LONG_TIMEOUT)
        
        # Simulate a lost connection
        print("Simulating connection lost...")
        page.context.set_offline(True)
                 
        # Verify the 'Lost Connection' page appears
        expect(page.get_by_role("heading", name="Connect with Internet")).to_be_visible()
        print("Test passed. Lost Connection page was displayed.")
        
    finally:
        page.context.set_offline(False)

    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)

# @pytest.mark.regression
# def test_auto_recovers_to_login_page_for_guest(page: Page, base_url):
#     """
#     Verifies that the application automatically recovers from a lost connection
#     and completes the intended navigation after the connection is restored.
#     """
#     try:
#         # 1. Open the main page
#         page.goto(base_url, timeout=LONG_TIMEOUT)
        
#         # 2. Simulate a lost connection
#         print("Simulating connection lost...")
#         page.context.set_offline(True)
            
#         # 4. Verify the 'Lost Connection' page appears
#         expect(page.get_by_role("heading", name="Connect with Internet")).to_be_visible()
#         print("Lost Connection page was displayed as expected.")
        
#         # 5. Restore the connection
#         print("Restoring connection...")
#         page.context.set_offline(False)
#         page.wait_for_timeout(6000)
#         # 6. Verify automatic recovery
#         #    We do not click anything, just wait for the application to recover
#         #    and continue the navigation to the Login page.
#         print("Waiting for auto-recovery and navigation to complete...")
        
#         # This assertion will wait until the heading on the Login page appears.
#         # If the page recovers automatically, this element will be visible.
#         expect(page.get_by_role("heading", name="Recommendation for You")).to_be_hidden(timeout=LONG_TIMEOUT)
        
#         print("Test passed. Page auto-recovered to the Login page successfully.")
        
#     finally:
#         # Ensure the connection is always back online at the end of the test
#         print("CLEANUP: Ensuring context is back online.")
#         page.context.set_offline(False)

#     # Add a 5-second pause to ensure the final state is recorded
#     page.wait_for_timeout(5000)

@pytest.mark.regression
def test_browser_back_button_on_lost_connection_page_for_guest(page: Page, base_url):
    """
    Verifies the system handles the browser's back button gracefully
    on the Lost Connection page.
    (Negative False Scenario)
    """
    try:
        page.goto(base_url, timeout=LONG_TIMEOUT)
        page.context.set_offline(True)
        
        lost_connection_heading = page.get_by_role("heading", name="Connect with Internet")
        expect(lost_connection_heading).to_be_visible()

        # Try using the browser's 'back' button
        print("Using browser's back button...")
        page.go_back()
        
        # NEW VERIFICATION: Ensure the page URL is now 'about:blank'
        print("Verifying that the current page is 'about:blank'...")
        expect(page).to_have_url("about:blank", timeout=MEDIUM_TIMEOUT)
        
    finally:
        page.context.set_offline(False)

    # Add a 5-second pause to ensure the final state is recorded
    page.wait_for_timeout(5000)

@pytest.mark.unit
def test_lost_connection_page_ui_elements(page: Page, base_url, take_screenshot):
    """
    Verifies that all key UI elements on the 'Lost Connection' page are
    present and visible, and takes a screenshot of each.
    """
    # --- THIS TEST IS UNCHANGED AS PER YOUR REQUEST ---
    try:
        # 1. Open the main page
        page.goto(base_url, timeout=LONG_TIMEOUT)
        
        # 2. Simulate a lost connection
        print("Simulating connection lost...")
        page.context.set_offline(True)

        # 4. Verify UI elements on the 'Lost Connection' page
        print("Verifying UI elements on the Lost Connection page...")
        
        # Verify and screenshot the Heading
        lost_connection_heading = page.get_by_role("heading", name="Connect with Internet")
        expect(lost_connection_heading).to_be_visible(timeout=MEDIUM_TIMEOUT)
        take_screenshot("heading_connect_with_internet_visible")
        print("  - Heading 'Connect with Internet' is visible.")

        # Verify and screenshot the Retry Button
        retry_button = page.get_by_role("button", name="Retry")
        expect(retry_button).to_be_visible(timeout=MEDIUM_TIMEOUT)
        take_screenshot("button_retry_visible")
        print("  - Button 'Retry' is visible.")
        
        print("\nUI Element test for Lost Connection page passed.")
    finally:
        # Ensure the connection is back to normal after the test is complete
        print("CLEANUP: Ensuring context is back online.")
        page.context.set_offline(False)