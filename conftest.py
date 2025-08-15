import os
from pathlib import Path
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

def pytest_addoption(parser):
    parser.addoption("--username", action="store", default=None, help="Username untuk login")
    parser.addoption("--password", action="store", default=None, help="Password untuk login")

load_dotenv()
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

RESULTS_DIR = Path("results")
VIDEOS_DIR = RESULTS_DIR / "videos"
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"

for folder in [VIDEOS_DIR, SCREENSHOTS_DIR]:
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

# --- PENDEKATAN FINAL UNTUK VIDEO ---
@pytest.fixture(scope="function")
def context(browser, request):
    # Langsung rekam ke direktori video utama. Playwright akan buat file temporer di sini.
    ctx = browser.new_context(
        record_video_dir=VIDEOS_DIR,
        viewport={'width': 1280, 'height': 720}
    )
    request.node.context = ctx
    
    yield ctx # Tes berjalan di sini
    
    # --- Logika Teardown untuk Memindahkan dan Menimpa Video ---
    video_temp_path = Path(ctx.pages[0].video.path()) if ctx.pages and ctx.pages[0].video else None
    ctx.close()
    
    rep = getattr(request.node, "rep_call", None)
    
    if rep and video_temp_path and video_temp_path.exists():
        try:
            status = "passed" if rep.passed else "failed"
            test_func_name = request.node.name
            test_module_name = Path(request.node.fspath).stem
            marker = next(request.node.iter_markers(), None)
            marker_name = marker.name if marker else "unmarked"

            video_dir_final = VIDEOS_DIR / marker_name / test_module_name / status
            video_dir_final.mkdir(parents=True, exist_ok=True)
            video_file_final = video_dir_final / f"{test_func_name}_{status}.webm"
            
            # Jika file tujuan sudah ada, hapus (timpa).
            if video_file_final.exists():
                video_file_final.unlink()
            
            # Pindahkan file video temporer ke lokasi dan nama final.
            video_temp_path.rename(video_file_final)
            print(f"\n[Video saved] {video_file_final}")

        except Exception as e:
            print(f"\n[Video process failed] {e}")

@pytest.fixture(scope="function")
def page(context, request):
    page = context.new_page()
    request.node.page = page
    yield page

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        item.rep_call = rep

    if rep.when == "call":
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