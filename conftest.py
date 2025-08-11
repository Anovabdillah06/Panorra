import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
BASE_URL = os.getenv('BASE_URL', 'https://dev.panorra.com/')
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

@pytest.fixture(scope='session')
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope='session')
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(
        headless=HEADLESS,
        slow_mo=0 if HEADLESS else 50
    )
    yield browser
    browser.close()

@pytest.fixture(scope='function')
def context(browser, request):
    # Ambil mark & nama fungsi test
    marks = [mark.name for mark in request.node.iter_markers()]
    marks_str = "_".join(marks) if marks else "nomark"
    test_name = request.node.name

    videos_dir = Path("videos") / marks_str
    videos_dir.mkdir(parents=True, exist_ok=True)

    # Record video
    ctx = browser.new_context(record_video_dir=str(videos_dir))
    request.node._video_dir = videos_dir
    request.node._video_name = f"{test_name}.webm"

    yield ctx

    # Rename video agar sesuai nama test
    try:
        for page in ctx.pages:
            video = page.video
            if video:
                path = Path(video.path())
                new_path = request.node._video_dir / request.node._video_name
                path.rename(new_path)
                print(f"[Video saved] {new_path}")
    except Exception as e:
        print(f"[Video save error] {e}")

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

# Screenshot tiap test
@pytest.hookimpl
def pytest_runtest_makereport(item, call):
    if call.when == 'call':
        page = getattr(item, 'page', None)
        if page:
            status = "passed" if call.excinfo is None else "failed"

            marks = [mark.name for mark in item.iter_markers()]
            marks_str = "_".join(marks) if marks else "nomark"

            screenshots_dir = Path('screenshots') / marks_str
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            filename = f"{item.name}_{status}.png"
            screenshot_path = screenshots_dir / filename

            try:
                page.screenshot(path=str(screenshot_path))
                print(f"[Screenshot saved] {screenshot_path}")
            except Exception as e:
                print(f"[Screenshot error] {e}")
