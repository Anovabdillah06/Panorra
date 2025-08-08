import time
from datetime import datetime

def wait(seconds: int):
    """Pause eksekusi dalam detik."""
    time.sleep(seconds)

def take_screenshot(page, name="screenshot"):
    """Ambil screenshot dan simpan di folder screenshots."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    page.screenshot(path=f"screenshots/{name}_{timestamp}.png")

def assert_text(page, selector, expected_text):
    """Assert teks elemen sesuai harapan."""
    element_text = page.inner_text(selector).strip()
    assert element_text == expected_text, f"Expected '{expected_text}' but got '{element_text}'"
