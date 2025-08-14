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
    # Hook wrapper untuk menyimpan hasil laporan akhir
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call':
        item.report = report

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    # Pindahkan video dari folder sementara ke folder hasil yang benar
    for item in session.items:
        context = getattr(item, 'context', None)
        if context:
            # Dapatkan laporan akhir tes
            report = getattr(item, 'report', None)
            if report:
                status = "passed" if report.passed else "failed"
                module_name = getattr(item, '_module_name', 'nomodule')
                marks_str = getattr(item, '_marks_str', 'nomark')
                
                final_video_dir = Path("results") / status / module_name / marks_str
                final_video_dir.mkdir(parents=True, exist_ok=True)
                
                for page in context.pages:
                    video = page.video
                    if video:
                        try:
                            filename_video = f"{item.name}.webm"
                            path_final = final_video_dir / filename_video
                            
                            video.save_as(path_final)
                            print(f"[Video saved] {path_final}")
                        except Exception as e:
                            print(f"[Video save error] {e}")

    # Bersihkan folder sementara setelah semua tes selesai
    temp_dir = Path("videos_temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)