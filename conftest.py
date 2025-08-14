import os
import shutil
from pathlib import Path
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# -------------------------------
# Load .env
# -------------------------------
# Memuat semua variabel dari file .env
load_dotenv()

# Membaca variabel dari environment.
# Menggunakan nama yang lebih spesifik (TEST_USERNAME, TEST_PASSWORD) adalah praktik terbaik
# untuk menghindari konflik dengan variabel sistem.
BASE_URL = os.getenv("BASE_URL", "https://dev.panorra.com/")
USERNAME = os.getenv("TEST_USERNAME")
PASSWORD = os.getenv("TEST_PASSWORD")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

# Menambahkan print untuk memastikan variabel dimuat dengan benar saat tes berjalan
print(f"--- TEST ENV LOADED ---")
print(f"URL: {BASE_URL}")
print(f"USER: {USERNAME}")
print(f"HEADLESS: {HEADLESS}")
print(f"-----------------------")


# -------------------------------
# Direktori Hasil Tes
# -------------------------------
RESULTS_DIR = Path("results")
VIDEOS_DIR = RESULTS_DIR / "videos"
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"
TEMP_VIDEO_DIR = RESULTS_DIR / "temp_videos"

# Membuat direktori jika belum ada
for folder in [VIDEOS_DIR, SCREENSHOTS_DIR, TEMP_VIDEO_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# -------------------------------
# Fixtures - Penyedia Data & Setup
# -------------------------------
@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def username():
    return USERNAME

@pytest.fixture(scope="session")
def password():
    return PASSWORD

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
        viewport={'width': 1280, 'height': 720} # Menambahkan viewport standar
    )
    request.node.context = ctx
    yield ctx
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

# -------------------------------
# Hooks - Aksi Otomatis Saat Tes Berjalan
# -------------------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        page = getattr(item, "page", None)
        if page and not page.is_closed():
            status = "passed" if rep.passed else "failed"
            ss_dir = SCREENSHOTS_DIR / status
            ss_dir.mkdir(parents=True, exist_ok=True)
            ss_file = ss_dir / f"{item.name}_{status}.png"
            try:
                page.screenshot(path=str(ss_file))
                print(f"\n[Screenshot saved] {ss_file}")
            except Exception as e:
                print(f"\n[Screenshot failed] {e}")

        ctx = getattr(item, "context", None)
        if ctx:
            for p in ctx.pages:
                if not p.is_closed() and p.video:
                    try:
                        path = Path(p.video.path())
                        video_file = VIDEOS_DIR / f"{item.name}.webm"
                        if video_file.exists():
                            video_file.unlink()
                        path.rename(video_file)
                        print(f"[Video saved] {video_file}")
                    except Exception as e:
                        print(f"[Video save failed] {e}")

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    if TEMP_VIDEO_DIR.exists():
        shutil.rmtree(TEMP_VIDEO_DIR)