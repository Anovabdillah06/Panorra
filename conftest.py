import os
import shutil
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

# --- PERBAIKAN FINAL UNTUK PENYIMPANAN VIDEO ---
@pytest.fixture(scope="function")
def context(browser, request):
    ctx = browser.new_context(
        record_video_dir=VIDEOS_DIR,  # Langsung rekam ke sub-folder sementara di dalam videos
        viewport={'width': 1280, 'height': 720}
    )
    request.node.context = ctx
    
    yield ctx # Tes berjalan di sini
    
    # --- Logika Teardown Baru ---
    rep = getattr(request.node, "rep_call", None)
    if not rep:
        ctx.close()
        return

    # Pastikan ada halaman dan objek video sebelum melanjutkan
    if ctx.pages and ctx.pages[0].video:
        try:
            # Tentukan path dan nama file final
            status = "passed" if rep.passed else "failed"
            test_func_name = request.node.name
            test_module_name = Path(request.node.fspath).stem

            video_dir_final = VIDEOS_DIR / test_module_name / status
            video_dir_final.mkdir(parents=True, exist_ok=True)
            video_file_final = video_dir_final / f"{test_func_name}_{status}.webm"
            
            # Gunakan metode save_as() yang andal SEBELUM menutup konteks
            ctx.pages[0].video.save_as(video_file_final)
            print(f"\n[Video saved] {video_file_final}")

            # Hapus file video temporer asli yang dibuat Playwright
            Path(ctx.pages[0].video.path()).unlink()

        except Exception as e:
            print(f"\n[Video save failed] {e}")
    
    # Terakhir, tutup konteks
    ctx.close()

@pytest.fixture(scope="function")
def page(context, request):
    page = context.new_page()
    request.node.page = page
    yield page
    try:
        page.close()
    except Exception:
        pass

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
            
            ss_dir = SCREENSHOTS_DIR / test_module_name / status
            ss_dir.mkdir(parents=True, exist_ok=True)
            
            ss_file = ss_dir / f"{test_func_name}_{status}.png"
            
            try:
                page.screenshot(path=str(ss_file))
                print(f"\n[Screenshot saved] {ss_file}")
            except Exception as e:
                print(f"\n[Screenshot failed] {e}")