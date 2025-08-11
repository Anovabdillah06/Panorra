import os
import shutil
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

    # Buat folder video
    videos_dir = Path("videos") / marks_str
    videos_dir.mkdir(parents=True, exist_ok=True)

    ctx = browser.new_context(record_video_dir=str(videos_dir))
    request.node._video_dir = videos_dir
    request.node._marks_str = marks_str

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

@pytest.hookimpl
def pytest_runtest_makereport(item, call):
    """Screenshot & Video setiap test (passed/failed)"""
    if call.when == 'call':
        status = "passed" if call.excinfo is None else "failed"
        marks_str = getattr(item, '_marks_str', 'nomark')

        # === Screenshot ===
        page = getattr(item, 'page', None)
        if page:
            screenshots_dir = Path('screenshots') / marks_str
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            filename_ss = f"{marks_str}_{item.name}_{status}.png"
            screenshot_path = screenshots_dir / filename_ss

            try:
                if screenshot_path.exists():
                    screenshot_path.unlink()
                page.screenshot(path=str(screenshot_path))
                print(f"[Screenshot saved] {screenshot_path}")

                # Copy ke root screenshots_root
                root_ss_dir = Path("screenshots_root") / marks_str
                root_ss_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(screenshot_path, root_ss_dir / filename_ss)
                print(f"[Screenshot copied to root] {root_ss_dir / filename_ss}")

            except Exception as e:
                print(f"[Screenshot error] {e}")

        # === Video ===
        ctx = getattr(item, 'context', None)
        if ctx:
            try:
                for page in ctx.pages:
                    video = page.video
                    if video:
                        path = Path(video.path())
                        filename_video = f"{marks_str}_{item.name}_{status}.webm"
                        new_path = Path("videos") / marks_str / filename_video

                        if new_path.exists():
                            new_path.unlink()
                        path.rename(new_path)
                        print(f"[Video saved] {new_path}")

                        # Copy ke root videos_root
                        root_video_dir = Path("videos_root") / marks_str
                        root_video_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(new_path, root_video_dir / filename_video)
                        print(f"[Video copied to root] {root_video_dir / filename_video}")

            except Exception as e:
                print(f"[Video save error] {e}")
