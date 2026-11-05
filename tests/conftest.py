import pytest

BASE_URL = "https://www.saucedemo.com"

USERNAME = "standard_user"
PASSWORD = "secret_sauce"


@pytest.fixture
def logged_in_page(page):
    """Login saucedemo ด้วย standard_user แล้ว return page ที่พร้อมใช้"""
    page.goto(BASE_URL)
    page.locator('[data-test="username"]').fill(USERNAME)
    page.locator('[data-test="password"]').fill(PASSWORD)
    page.locator('[data-test="login-button"]').click()

    # รอให้ navigate ไปหน้า inventory สำเร็จ
    page.wait_for_url("**/inventory.html")
    return page