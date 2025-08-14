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

# Pastikan folder results ada sebelum test mulai
def pytest_configure(config):
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    # Buat .gitkeep supaya folder ikut ke repo
    gitkeep = results_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()

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

# Hook untuk simpan hasil report test
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        item.rep_call = rep

@pytest.fixture(scope='function')
def context(browser, request):
    module_name = Path(request.fspath).stem
    marks = [mark.name for mark in request.node.iter_markers()]
    marks_str = "_".join(marks) if marks else "nomark"

    request.node._module_name = module_name
    request.node._marks_str = marks_str

    # Folder video sementara
    video_temp_dir = Path("videos_temp")
    video_temp_dir.mkdir(parents=True, exist_ok=True)

    ctx = browser.new_context(record_video_dir=str(video_temp_dir))
    request.node.context = ctx
    yield ctx

    # Tentukan status setelah test selesai
    status = "passed" if getattr(request.node, "rep_call", None) and request.node.rep_call.passed else "failed"
    final_video_dir = Path("results") / status / module_name / marks_str
    final_video_dir.mkdir(parents=True, exist_ok=True)

    for page in ctx.pages:
        video = page.video
        if video:
            try:
                filename_video = f"{request.node.name}.webm"
                path_final = final_video_dir / filename_video
                video.save_as(path_final)
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

# Screenshot otomatis setelah setiap test
@pytest.fixture(scope='function', autouse=True)
def capture_screenshot_after_test(request):
    yield
    page = getattr(request.node, "page", None)
    if page:
        status = "passed" if getattr(request.node, "rep_call", None) and request.node.rep_call.passed else "failed"
        module_name = getattr(request.node, "_module_name", "unknown")
        marks_str = getattr(request.node, "_marks_str", "nomark")

        screenshot_dir = Path("results") / status / module_name / marks_str
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = screenshot_dir / f"{request.node.name}.png"
        try:
            page.screenshot(path=str(screenshot_path))
            print(f"[Screenshot saved] {screenshot_path}")
        except Exception as e:
            print(f"[Screenshot save error] {e}")

# Bersihkan folder video sementara di akhir session
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    temp_dir = Path("videos_temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
