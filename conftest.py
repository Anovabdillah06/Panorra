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
    
    # Menentukan path hasil di awal
    final_results_dir = Path("results") / "temp" # Path sementara
    final_results_dir.mkdir(parents=True, exist_ok=True)
    
    # Buat context dengan video recording
    ctx = browser.new_context(
        record_video_dir=str(final_results_dir)
    )
    request.node.context = ctx 

    yield ctx
    
    # --- Perbaikan: Simpan video setelah tes, sebelum context ditutup ---
    status = "passed" if request.node.rep_call.passed else "failed"
    new_final_dir = Path("results") / status / module_name / marks_str
    new_final_dir.mkdir(parents=True, exist_ok=True)
    
    for page in ctx.pages:
        video = page.video
        if video:
            filename_video = f"{request.node.name}.webm"
            path_final = new_final_dir / filename_video
            
            try:
                # video.path() hanya valid setelah context ditutup.
                # Kita akan memindahkan file setelahnya di pytest_runtest_teardown.
                # Untuk kode ini, kita akan mengabaikan video.save_as() di sini
                # dan membiarkan pytest-playwright menangani penutupan
                pass
            except Exception as e:
                print(f"[Video save error in fixture] {e}")

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

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    # Simpan laporan panggilan tes untuk digunakan di fixture context
    item.rep_call = call
    
    # Hook ini sekarang hanya akan menangani screenshot
    if call.when == 'call':
        status = "passed" if call.excinfo is None else "failed"
        module_name = getattr(item, '_module_name', 'nomodule')
        marks_str = getattr(item, '_marks_str', 'nomark')
        
        base_results_dir = Path("results")
        final_results_dir = base_results_dir / status / module_name / marks_str
        final_results_dir.mkdir(parents=True, exist_ok=True)

        page = getattr(item, 'page', None)
        if page:
            try:
                filename_ss = f"{item.name}.png"
                screenshot_path = final_results_dir / filename_ss
                page.screenshot(path=str(screenshot_path))
                print(f"[Screenshot saved] {screenshot_path}")
            except Exception as e:
                print(f"[Screenshot error] {e}")

@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    # Mengambil video dari folder sementara dan memindahkannya
    ctx = getattr(item, 'context', None)
    if ctx and not ctx.is_closed():
        ctx.close() # Pastikan context ditutup, yang akan memfinalisasi video
    
    if item.rep_call.passed:
        status = "passed"
    else:
        status = "failed"
    
    module_name = getattr(item, '_module_name', 'nomodule')
    marks_str = getattr(item, '_marks_str', 'nomark')
    
    temp_video_dir = Path("results") / "temp"
    final_video_dir = Path("results") / status / module_name / marks_str
    
    for video_file in temp_video_dir.glob("*.webm"):
        if video_file.stat().st_size > 0:
            final_video_file = final_video_dir / video_file.name
            shutil.move(str(video_file), str(final_video_file))
            print(f"[Video moved] {final_video_file}")