import os
import shutil
import pytest
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load .env jika ada
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
    module_name = Path(request.fspath).stem
    marks = [mark.name for mark in request.node.iter_markers()]
    marks_str = "_".join(marks) if marks else "nomark"
    
    # Simpan nama modul dan mark di `request` agar bisa diakses di hook
    request.node._module_name = module_name
    request.node._marks_str = marks_str
    
    # Simpan video ke direktori sementara
    ctx = browser.new_context(record_video_dir="videos_temp")
    request.node.context = ctx 

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

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call':
        item.report = report

@pytest.hookimpl
def pytest_runtest_teardown(item, nextitem):
    # Mengambil status dari report yang disimpan
    status = "passed" if getattr(item, 'report', None) and item.report.passed else "failed"
    
    module_name = getattr(item, '_module_name', 'nomodule')
    marks_str = getattr(item, '_marks_str', 'nomark')
    
    base_results_dir = Path("results")
    final_results_dir = base_results_dir / status / module_name / marks_str
    final_results_dir.mkdir(parents=True, exist_ok=True)
    
    # === Screenshot ===
    page = getattr(item, 'page', None)
    if page and page.is_closed():
        try:
            filename_ss = f"{item.name}.png"
            screenshot_path = final_results_dir / filename_ss
            page.screenshot(path=str(screenshot_path))
            print(f"[Screenshot saved] {screenshot_path}")
        except Exception as e:
            print(f"[Screenshot error] {e}")
            
    # === Video ===
    ctx = getattr(item, 'context', None)
    if ctx:
        try:
            for p in ctx.pages:
                video = p.video
                if video:
                    filename_video = f"{item.name}.webm"
                    path_final = final_results_dir / filename_video
                    
                    video.save_as(path_final)
                    print(f"[Video saved] {path_final}")
        except Exception as e:
            print(f"[Video save error] {e}")

# Hook ini akan membersihkan folder sementara setelah semua tes selesai
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    temp_dir = Path("videos_temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)