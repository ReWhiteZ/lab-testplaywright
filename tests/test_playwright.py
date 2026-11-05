import pytest

BASE_URL = "https://www.saucedemo.com"

USERNAME = "standard_user"
PASSWORD = "secret_sauce"

def _parse_price(price_text: str) -> float:
    """แปลง '$29.99' -> 29.99"""
    return float(price_text.replace("$", "").strip())

def _extract_money(locator) -> float:
    """ดึงตัวเลขจากข้อความ 'Item total: $40.00' -> 40.00"""
    text = locator.text_content()       
    return float(text.split("$")[-1].strip())

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

def test_login_success(logged_in_page):
    page = logged_in_page
    assert "/inventory.html" in page.url, f"URL ไม่ใช่ inventory: {page.url}"
    assert page.locator(".title").text_content() == "Products"

def test_sort_price_high_to_low(logged_in_page):
    page = logged_in_page

    # เปลี่ยน sort เป็น "Price (high to low)"  ->  value = "hilo"
    page.locator('[data-test="product-sort-container"]').select_option("hilo")

    # ดึงราคาสินค้าทุกชิ้นบนหน้า ณ ตอนนี้ (Dynamic Inspection)
    price_texts = page.locator('[data-test="inventory-item-price"]').all_text_contents()
    prices = [_parse_price(t) for t in price_texts]

    # ต้องมีอย่างน้อย 2 ชิ้นถึงจะเทียบได้
    assert len(prices) >= 2, f"ต้องมีสินค้าอย่างน้อย 2 ชิ้น แต่เจอ {len(prices)}"

    # ตรวจว่าชิ้นแรก >= ชิ้นถัดไป
    assert prices[0] >= prices[1], (
        f"หลัง sort high->low ราคาชิ้นแรก ({prices[0]}) "
        f"ต้อง >= ชิ้นถัดไป ({prices[1]})"
    )

def test_full_checkout_flow(logged_in_page):
    page = logged_in_page

    # --- Step 1: เรียงราคาจากมากไปน้อย ---
    page.locator('[data-test="product-sort-container"]').select_option("hilo")

    items = page.locator('[data-test="inventory-item"]')
    first_item = items.first       # แพงที่สุด (เพราะ sort hilo)
    last_item = items.last         # ถูกที่สุด

    # --- Step 2: ดึงราคาของ 2 ชิ้นนี้ไปใช้ตรวจใน checkout ---
    max_price = _parse_price(
        first_item.locator('[data-test="inventory-item-price"]').text_content()
    )
    min_price = _parse_price(
        last_item.locator('[data-test="inventory-item-price"]').text_content()
    )

    # --- Step 3: เพิ่มทั้ง 2 ชิ้นลงตะกร้า ---
    first_item.locator('button:has-text("Add to cart")').click()
    last_item.locator('button:has-text("Add to cart")').click()

    # --- Step 4: ตรวจ Badge ตะกร้า = 2 ---
    badge = page.locator('[data-test="shopping-cart-badge"]')
    assert badge.text_content() == "2", (
        f"Badge ควรเป็น '2' แต่เจอ '{badge.text_content()}'"
    )
    
    # --- Step 5: ไปหน้า Cart ---
    page.locator('[data-test="shopping-cart-link"]').click()
    page.wait_for_url("**/cart.html")

    # --- Step 6: ตรวจว่ามี 2 ชิ้น "ตามที่เลือกไว้" (เทียบราคา) ---
    cart_prices = sorted(
        _parse_price(t)
        for t in page.locator('[data-test="inventory-item-price"]').all_text_contents()
    )
    expected_prices = sorted([max_price, min_price])

    assert len(cart_prices) == 2, (
        f"ตะกร้าควรมี 2 ชิ้น แต่เจอ {len(cart_prices)}"
    )
    for actual, expected in zip(cart_prices, expected_prices):
        assert abs(actual - expected) < 0.01, (
            f"ราคาในตะกร้า {cart_prices} ไม่ตรงกับที่เลือกไว้ {expected_prices}"
        )

    # --- Step 7: กด Checkout ---
    page.locator('[data-test="checkout"]').click()
    page.wait_for_url("**/checkout-step-one.html")

    # --- Step 8: กรอกข้อมูลผู้ซื้อ ---
    page.locator('[data-test="firstName"]').fill("Test")
    page.locator('[data-test="lastName"]').fill("User")
    page.locator('[data-test="postalCode"]').fill("10110")
    page.locator('[data-test="continue"]').click()
    page.wait_for_url("**/checkout-step-two.html")

    # --- Step 9: ดึง Item Total / Tax / Total จากหน้า Overview ---
    subtotal = _extract_money(page.locator('[data-test="subtotal-label"]'))
    tax      = _extract_money(page.locator('[data-test="tax-label"]'))
    total    = _extract_money(page.locator('[data-test="total-label"]'))

    # --- Step 10: ตรวจ Item Total = sum ของ 2 ชิ้นที่เลือกไว้ ---
    expected_subtotal = max_price + min_price
    assert abs(subtotal - expected_subtotal) < 0.01, (
        f"Item Total ({subtotal}) ไม่ตรงกับ {max_price} + {min_price} = {expected_subtotal}"
    )

    # --- Step 11: ตรวจ Tax ≈ 8% ของ Item Total ---
    expected_tax = subtotal * 0.08
    assert abs(tax - expected_tax) < 0.02, (
        f"Tax ({tax}) ไม่ตรงกับ 8% ของ {subtotal} (คำนวณได้ {expected_tax:.4f})"
    )

    # --- Step 12: ตรวจ Item Total + Tax == Total ---
    assert abs((subtotal + tax) - total) < 0.01, (
        f"{subtotal} + {tax} = {subtotal + tax} ไม่เท่ากับ Total ({total})"
    )

    # --- Step 13: กด Finish ---
    page.locator('[data-test="finish"]').click()

    # --- Step 14: Assert URL ปัจจุบันคือหน้า complete ---
    page.wait_for_url("**/checkout-complete.html")
    assert page.url == "https://www.saucedemo.com/checkout-complete.html", (
        f"URL ไม่ใช่ checkout-complete.html แต่เป็น: {page.url}"
    )

    # --- Step 15: ตรวจข้อความ Thank you ---
    complete_header = page.locator('[data-test="complete-header"]')
    assert complete_header.text_content() == "Thank you for your order!", (
        f"ข้อความไม่ตรง: '{complete_header.text_content()}'"
    )