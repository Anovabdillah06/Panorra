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
    
    request.node._module_name = module_name
    request.node._marks_str = marks_str
    
    # Simpan video ke direktori sementara di root proyek
    video_temp_dir = Path("videos_temp")
    video_temp_dir.mkdir(parents=True, exist_ok=True)
    ctx = browser.new_context(record_video_dir=str(video_temp_dir))
    request.node.context = ctx 

    yield ctx
    
    # --- PERBAIKAN PENTING DI SINI ---
    # Logika untuk menyimpan video dipindahkan ke sini
    # Ini memastikan kode dijalankan setelah tes selesai, tetapi sebelum context ditutup
    status = "passed" if request.node.rep_call.passed else "failed"
    final_results_dir = Path(os.getcwd()) / "results" / status / module_name / marks_str
    final_results_dir.mkdir(parents=True, exist_ok=True)
    
    for page in ctx.pages:
        video = page.video
        if video:
            try:
                path_temp = Path(video.path())
                filename_video = f"{request.node.name}.webm"
                path_final = final_results_dir / filename_video
                
                # Gunakan shutil.move karena Playwright sudah melepaskan file setelah page/context ditutup
                shutil.move(path_temp, path_final)
                print(f"[Video saved] {path_final}")
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

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call':
        item.rep_call = call
        status = "passed" if report.passed else "failed"
        module_name = getattr(item, '_module_name', 'nomodule')
        marks_str = getattr(item, '_marks_str', 'nomark')

        base_results_dir = Path(os.getcwd()) / "results"
        final_results_dir = base_results_dir / status / module_name / marks_str
        final_results_dir.mkdir(parents=True, exist_ok=True)

        page = getattr(item, 'page', None)
        if page and not page.is_closed():
            try:
                filename_ss = f"{item.name}.png"
                screenshot_path = final_results_dir / filename_ss
                page.screenshot(path=str(screenshot_path))
                print(f"[Screenshot saved] {screenshot_path}")
            except Exception as e:
                print(f"[Screenshot error] {e}")