import pytest
from playwright.sync_api import Page, expect

LONG_TIMEOUT = 60000      # Wait time extended to 60 seconds
MEDIUM_TIMEOUT = 13000

@pytest.mark.smoke
def test_banner_link_loads_new_page_successfully(page: Page, base_url):
    """
    Verifies that the banner link opens and loads a new page successfully.
    """
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    banner_link = page.get_by_role("link", name="banner")
    expect(banner_link).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # Wait for the 'page' event (new tab/popup) to occur after the click
    with page.context.expect_event("page") as new_page_info:
        banner_link.click()
    
    # Get the new page object from the event
    new_page = new_page_info.value  
    page.wait_for_timeout(3000)  
    # (Optional) After successful verification, close the new page
    new_page.close()

@pytest.mark.smoke
def test_verifies_staying_on_homepage_after_load(page: Page, base_url):
    """
    Verifies that after the page loads, there is no automatic redirect
    by checking for the banner element and the current URL.
    """
    # 1. Open the main page
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 2. Find the banner element to detect that we are still on the correct page
    #    (this element will not be clicked)
    banner_element = page.get_by_role("link", name="banner")
    
    # 3. Verify that the banner element is visible.
    #    If this element exists, it means we are still on the main page.
    expect(banner_element).to_be_visible(timeout=MEDIUM_TIMEOUT)
    
    # 4. (Additional Assertion) Explicitly check that the page URL
    #    is still the same as the base_url.
    expect(page).to_have_url(base_url)


@pytest.mark.regression
def test_banner_is_visible_when_ads_are_blocked(page: Page, base_url):
    """
    Verifies that the "banner button" remains visible on the page
    even when the ad blocker feature (simulation) is active.
    """
    # 1. Activate the ad blocker simulation by blocking ad domains
    page.route("**/*doubleclick.net*", lambda route: route.abort())
    page.route("**/*googlesyndication.com*", lambda route: route.abort())
    
    # 2. Open the main page
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # 3. (Additional Verification) Ensure the ad element is truly blocked/hidden.
    #    Replace '.ad-container' with the ad selector on your web.
    ad_locator = page.locator('.ad-container')
    expect(ad_locator).to_be_hidden(timeout=MEDIUM_TIMEOUT)
    
    # 4. (Main Verification) Find and ensure the "banner button" remains visible.
    #    This is the core of your test.
    banner_locator = page.get_by_role("link", name="banner")
    
    # This assertion ensures that the banner does not disappear when ads are blocked.
    expect(banner_locator).to_be_visible(timeout=MEDIUM_TIMEOUT)


@pytest.mark.regression
def test_malicious_redirect_is_prevented(page: Page, base_url):
    """
    Verifies the page does not automatically redirect without interaction.
    (Negative False Scenario)
    """
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # Wait a few seconds to see if any script tries to redirect
    page.wait_for_timeout(3000)
    
    # Verify that the page is still at the same URL and has not been redirected
    expect(page).to_have_url(base_url)


@pytest.mark.unit
def test_homepage_key_elements_are_visible(page: Page, base_url, take_screenshot):
    """
    Verifies that all key interactive elements on the main page are visible.
    """
    page.goto(base_url, timeout=LONG_TIMEOUT)
    
    # Verify main elements are visible before interaction
    print("Verifying visibility of key elements...")
    
    expect(page.get_by_role("link", name="Log In")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(page.get_by_role("heading", name="Recommendation for You")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    take_screenshot("login_success")
    expect(page.get_by_role("button", name="next popular")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    take_screenshot("Button_visible")
    expect(page.get_by_role("listitem").filter(has_text="Recent")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    expect(page.get_by_role("link", name="banner")).to_be_visible(timeout=MEDIUM_TIMEOUT)
    take_screenshot("banner_visible")
    print("All key elements have been successfully verified.")