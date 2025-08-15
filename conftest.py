import os
import shutil
from pathlib import Path
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# --- TAMBAHAN: Fungsi untuk menerima argumen dari command-line ---
def pytest_addoption(parser):
    """Menambahkan opsi command-line kustom ke Pytest."""
    parser.addoption("--username", action="store", default=None, help="Username untuk login")
    parser.addoption("--password", action="store", default=None, help="Password untuk login")

# -------------------------------
# Load .env
# -------------------------------
load_dotenv()
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"


# -------------------------------
# Direktori Hasil Tes
# -------------------------------
RESULTS_DIR = Path("results")
VIDEOS_DIR = RESULTS_DIR / "videos"
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"
TEMP_VIDEO_DIR = RESULTS_DIR / "temp_videos"

for folder in [VIDEOS_DIR, SCREENSHOTS_DIR, TEMP_VIDEO_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# -------------------------------
# Fixtures - Penyedia Data & Setup
# -------------------------------
@pytest.fixture(scope="session")
def base_url(request):
    """Mendapatkan base_url dari command-line atau .env."""
    return request.config.getoption("--base-url") or os.getenv("BASE_URL", "https://dev.panorra.com/")

@pytest.fixture(scope="session")
def username(request):
    """Mendapatkan username dari command-line atau .env."""
    return request.config.getoption("--username") or os.getenv("TEST_USERNAME")

@pytest.fixture(scope="session")
def password(request):
    """Mendapatkan password dari command-line atau .env."""
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
    ctx = browser.new_context(
        record_video_dir=str(TEMP_VIDEO_DIR),
        viewport={'width': 1280, 'height': 720}
    )
    request.node.context = ctx
    
    yield ctx # Tes berjalan di sini
    
    # --- LOGIKA PENYIMPANAN VIDEO BARU ---
    # Dapatkan hasil tes (status) yang sudah disimpan di hook
    rep = getattr(request.node, "rep_call", None)
    if not rep:
        ctx.close()
        return

    # Dapatkan path video SEBELUM konteks ditutup
    video_path_obj = Path(ctx.pages[0].video.path()) if ctx.pages and ctx.pages[0].video else None
    ctx.close()

    if video_path_obj and video_path_obj.exists():
        try:
            status = "passed" if rep.passed else "failed"
            test_func_name = request.node.name
            # Dapatkan nama file tes (misal: "test_login")
            test_module_name = Path(request.node.fspath).stem

            # Buat struktur direktori baru
            video_dir_final = VIDEOS_DIR / test_module_name / status
            video_dir_final.mkdir(parents=True, exist_ok=True)
            
            # Buat nama file baru dengan status
            video_file_final = video_dir_final / f"{test_func_name}_{status}.webm"
            
            if video_file_final.exists():
                video_file_final.unlink()
            video_path_obj.rename(video_file_final)
            print(f"\n[Video saved] {video_file_final}")
        except Exception as e:
            print(f"\n[Video save failed] {e}")

@pytest.fixture(scope="function")
def page(context, request):
    page = context.new_page()
    request.node.page = page
    yield page
    try:
        page.close()
    except Exception:
        pass

# -------------------------------
# Hooks - (SEKARANG HANYA UNTUK SCREENSHOT)
# -------------------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    # Simpan hasil tes (rep) ke dalam item agar bisa diakses oleh fixture
    if rep.when == "call":
        item.rep_call = rep

    if rep.when == "call":
        page = getattr(item, "page", None)
        if page and not page.is_closed():
            # --- LOGIKA PENYIMPANAN SCREENSHOT BARU ---
            status = "passed" if rep.passed else "failed"
            test_func_name = item.name
            # Dapatkan nama file tes (misal: "test_login")
            test_module_name = Path(item.fspath).stem
            
            # Buat struktur direktori baru
            ss_dir = SCREENSHOTS_DIR / test_module_name / status
            ss_dir.mkdir(parents=True, exist_ok=True)
            
            # Buat nama file baru
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