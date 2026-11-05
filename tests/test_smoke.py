def test_login_success(logged_in_page):
    page = logged_in_page
    assert "/inventory.html" in page.url, f"URL ไม่ใช่ inventory: {page.url}"
    assert page.locator(".title").text_content() == "Products"