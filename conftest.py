import os
import shutil
from pathlib import Path
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page
import subprocess

def pytest_addoption(parser):
    parser.addoption("--username", action="store", default=None, help="Username untuk login")
    parser.addoption("--password", action="store", default=None, help="Password untuk login")

load_dotenv()
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

RESULTS_DIR = Path("results")
VIDEOS_DIR = RESULTS_DIR / "videos"
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"
TEMP_VIDEO_DIR = RESULTS_DIR / "temp_videos"

for folder in [VIDEOS_DIR, SCREENSHOTS_DIR, TEMP_VIDEO_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url") or os.getenv("BASE_URL", "https://dev.panorra.com/")

@pytest.fixture(scope="session")
def username(request):
    return request.config.getoption("--username") or os.getenv("TEST_USERNAME")

@pytest.fixture(scope="session")
def password(request):
    return request.config.getoption("--password") or os.getenv("TEST_PASSWORD")

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=HEADLESS)
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def context(browser, request):
    # Cek apakah tes memiliki marker 'unit'
    is_unit_test = request.node.get_closest_marker("unit") is not None
    
    context_args = {"viewport": {'width': 1280, 'height': 720}}

    # Hanya rekam video jika BUKAN tes unit
    if not is_unit_test:
        context_args["record_video_dir"] = str(TEMP_VIDEO_DIR)

    ctx = browser.new_context(**context_args)
    request.node.context = ctx
    
    yield ctx
    
    video_path = Path(ctx.pages[0].video.path()) if ctx.pages and ctx.pages[0].video else None
    ctx.close()
    
    rep = getattr(request.node, "rep_call", None)
    
    if rep and video_path and video_path.exists():
        try:
            status = "passed" if rep.passed else "failed"
            test_func_name = request.node.name
            test_module_name = Path(request.node.fspath).stem
            marker = next(request.node.iter_markers(), None)
            marker_name = marker.name if marker else "unmarked"

            video_dir_final = VIDEOS_DIR / marker_name / test_module_name / status
            video_dir_final.mkdir(parents=True, exist_ok=True)
            
            # Ubah ekstensi file tujuan menjadi .mp4
            video_file_final = video_dir_final / f"{test_func_name}_{status}.mp4"
            
            # Buat perintah untuk konversi menggunakan FFmpeg
            command = [
                "ffmpeg",
                "-i", str(video_path),
                "-y",
                "-loglevel", "error",
                str(video_file_final)
            ]
            
            # Jalankan perintah konversi
            subprocess.run(command, check=True)
            
            print(f"\n[Video converted to MP4] {video_file_final}")

        except Exception as e:
            print(f"\n[Video conversion to MP4 failed] {e}")

@pytest.fixture(scope="function")
def page(context, request):
    page = context.new_page()
    request.node.page = page
    yield page

@pytest.fixture
def take_screenshot(request, page: Page):
    screenshot_counter = 0
    test_func_name = request.node.name
    test_module_name = Path(request.node.fspath).stem
    marker = next(request.node.iter_markers(), None)
    marker_name = marker.name if marker else "unmarked"
    status = "passed"
    base_path = Path(f"results/screenshots/{marker_name}/{test_module_name}/{status}/")
    base_path.mkdir(parents=True, exist_ok=True)

    def _take_screenshot(step_description: str):
        nonlocal screenshot_counter
        screenshot_counter += 1
        file_name = f"{test_func_name}_{screenshot_counter:02d}_{step_description}.png"
        page.screenshot(path=base_path / file_name)

    yield _take_screenshot

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        item.rep_call = rep

    # Screenshot otomatis hanya berjalan jika BUKAN tes unit
    is_unit_test = item.get_closest_marker("unit") is not None
    if rep.when == "call" and not is_unit_test:
        page = getattr(item, "page", None)
        if page and not page.is_closed():
            status = "passed" if rep.passed else "failed"
            test_func_name = item.name
            test_module_name = Path(item.fspath).stem
            marker = next(item.iter_markers(), None)
            marker_name = marker.name if marker else "unmarked"
            
            ss_dir = SCREENSHOTS_DIR / marker_name / test_module_name / status
            ss_dir.mkdir(parents=True, exist_ok=True)
            ss_file = ss_dir / f"{test_func_name}_{status}.png"
            
            try:
                page.screenshot(path=str(ss_file))
                print(f"\n[Screenshot saved] {ss_file}")
            except Exception as e:
                print(f"\n[Screenshot failed] {e}")

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    if TEMP_VIDEO_DIR.exists():
        shutil.rmtree(TEMP_VIDEO_DIR)