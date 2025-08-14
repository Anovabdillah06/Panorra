import os
import shutil
from pathlib import Path
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load env file jika ada
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

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        item.rep_call = rep

@pytest.fixture(scope='function')
def context(browser, request):
    module = Path(request.fspath).stem
    marks = [m.name for m in request.node.iter_markers()]
    mark = marks[0] if marks else "nomark"
    request.node._module = module
    request.node._mark = mark

    video_temp = Path("videos_temp")
    video_temp.mkdir(parents=True, exist_ok=True)
    ctx = browser.new_context(record_video_dir=str(video_temp))
    request.node.context = ctx
    yield ctx

    status = "passed" if getattr(request.node, "rep_call", None) and request.node.rep_call.passed else "failed"
    video_dir = Path("results/videos") / module / status / mark
    video_dir.mkdir(parents=True, exist_ok=True)

    for page in ctx.pages:
        video = page.video
        if video:
            fn = f"{request.node.name}_{status}.webm"
            dest = video_dir / fn
            video.save_as(dest)
            print(f"[Video saved] {dest}")
    ctx.close()

@pytest.fixture(scope='function')
def page(context, request):
    p = context.new_page()
    request.node.page = p
    yield p
    try:
        p.close()
    except:
        pass

@pytest.fixture(scope='function', autouse=True)
def capture_screenshot(request):
    yield
    page = getattr(request.node, "page", None)
    if page:
        status = "passed" if getattr(request.node, "rep_call", None) and request.node.rep_call.passed else "failed"
        module = getattr(request.node, "_module", "unknown")
        mark = getattr(request.node, "_mark", "nomark")

        ss_dir = Path("results/screenshots") / module / status / mark
        ss_dir.mkdir(parents=True, exist_ok=True)
        ss_file = ss_dir / f"{request.node.name}_{status}.png"
        page.screenshot(path=str(ss_file))
        print(f"[Screenshot saved] {ss_file}")

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    tmp = Path("videos_temp")
    if tmp.exists():
        shutil.rmtree(tmp)

