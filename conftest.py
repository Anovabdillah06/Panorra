import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
BASE_URL = os.getenv('BASE_URL', 'https://dev.panorra.com/')
HEADLESS = os.getenv('HEADLESS', 'false').lower() in ('1', 'true', 'yes')


@pytest.fixture(scope='session')
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope='session')
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=HEADLESS, slow_mo=0 if HEADLESS else 50)
    yield browser
    browser.close()


@pytest.fixture(scope='session')
def context(browser):
    ctx = browser.new_context()
    yield ctx
    ctx.close()


@pytest.fixture(scope='function')
def page(context, request):
    page = context.new_page()
    request.node.page = page
    yield page
    try:
        page.close()
    except Exception:
        pass


# Screenshot untuk semua hasil test (pass & fail)
@pytest.hookimpl
def pytest_runtest_makereport(item, call):
    if call.when == 'call':
        page = getattr(item, 'page', None)
        if page:
            status = "passed" if call.excinfo is None else "failed"
            screenshots_dir = Path('screenshots') / status
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            path = screenshots_dir / f"{item.name}_{status}.png"
            try:
                page.screenshot(path=str(path))
                print(f"\n[Screenshot saved] {path}")
            except Exception as e:
                print(f"\n[Failed saving screenshot] {e}")
