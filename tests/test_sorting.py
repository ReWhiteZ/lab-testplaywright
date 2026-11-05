def _parse_price(price_text: str) -> float:
    """แปลง '$29.99' -> 29.99"""
    return float(price_text.replace("$", "").strip())


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