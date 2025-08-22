from playwright.sync_api import sync_playwright

def launch_browser(headless=True):
    """
    Launch Chrome browser instance (Playwright 'chromium' with channel='chrome').
    :param headless: True untuk tanpa UI, False untuk tampilkan browser
    """
    pw = sync_playwright().start()

    # Chromium dengan channel 'chrome' = Google Chrome
    browser = pw.chromium.launch(headless=headless, channel="chrome")

    header_array=[
        ("Access-Code", "NYQLFxYsnOy+/zwnNWmNTUN5")
    ]

    header_dic = dict(header_array)

    context = browser.new_context(
        extra_http_headers=header_dic
        
    )
    page = context.new_page()
    return pw, browser, context, page
