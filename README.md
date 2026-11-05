# Lab 05 — Playwright กับ Python และ pytest

คู่มือสร้าง browser test ด้วย Playwright Python และ pytest ตั้งแต่เริ่มต้น อธิบายแนวคิดของ fixture, locator, action และ assertion โดยไม่ผูกกับโจทย์ของเว็บใด

## สิ่งที่ต้องมี

- Python 3.14 (โปรเจกต์นี้กำหนด `requires-python = ">=3.14"`)
- `uv`
- Browser ที่ Playwright รองรับ (ติดตั้งผ่านคำสั่ง Playwright ด้านล่าง)

ติดตั้ง `uv` ตามเอกสารทางการ แล้วตรวจสอบด้วย `python --version` และ `uv --version`

## สร้างโปรเจกต์จากศูนย์

```powershell
uv init --package --python 3.14 playwright-python-tests
cd playwright-python-tests
uv add --dev pytest pytest-playwright
uv run playwright install chromium
New-Item -ItemType Directory tests
```

`pytest-playwright` ให้ fixture เช่น `page` สำหรับแต่ละ browser test ส่วนคำสั่ง `playwright install` จะติดตั้ง browser binary ที่ Playwright משתמש בו. אם רוצים דפדפנים נוספים, ניתן להריץ `uv run playwright install` בלי לציין דפדפן.

ตัวอย่าง `tests/test_example.py`:

```python
def test_example_heading(page):
    page.goto("https://example.com")
    heading = page.get_by_role("heading", name="Example Domain")
    assert heading.is_visible()
```

ตั้งชื่อไฟล์ `test_*.py` และฟังก์ชัน `test_*` เพื่อให้ pytest ค้นพบ

## โครงสร้างโปรเจกต์ตัวอย่าง

```text
playwright-python-tests/
├── src/playwright_python_tests/
├── tests/
│   └── test_example.py
├── pyproject.toml
└── uv.lock
```

ในงานจริงสามารถเพิ่ม `tests/conftest.py` เพื่อประกาศ fixture ใช้ร่วมกัน เช่น การสร้าง context หรือ helper สำหรับ sign-in และเก็บค่า base URL ใน configuration แทนการเขียนซ้ำ

## หลักการเขียน Playwright test

- `page` แทนหน้าหนึ่งหน้าใน browser ที่ fixture จัดการ lifecycle ให้
- ใช้ locator เช่น `get_by_role`, `get_by_label`, `get_by_text` หรือ `locator('[data-test="..."]')`
- ทำ action เช่น `click()`, `fill()` และ `select_option()` ผ่าน locator
- Playwright รอ locator/actionability ให้อัตโนมัติในหลายกรณี จึงไม่ควรเพิ่ม `sleep` โดยไม่จำเป็น
- ใช้ assertion ของ pytest (`assert`) และตรวจสิ่งที่ผู้ใช้สังเกตได้ เช่น URL, heading หรือสถานะ element
- ใช้ fixture ของ pytest สำหรับ setup ที่ใช้ซ้ำ แทนการคัดลอกขั้นตอนเตรียมหน้าทดสอบไปทุก test

## ติดตั้งและรันโปรเจกต์นี้

```powershell
uv sync
uv run playwright install chromium
uv run pytest
```

รัน test เฉพาะไฟล์หรือเลือก test ได้ด้วย:

```powershell
uv run pytest tests/test_smoke.py -v
uv run pytest -k sorting -v
```

เมื่อรันผ่าน Playwright pytest plugin จะเปิด browser แบบ headless ตามปกติ หากต้องการเห็น browser ให้ใช้ `--headed`:

```powershell
uv run pytest --headed
```

## แนวทางที่ควรทำ

- เลือก locator ที่สื่อความหมายและทนต่อการเปลี่ยน layout เช่น role/label หรือ `data-test`
- ใช้ fixture แบ่ง setup และ cleanup ให้ test อ่านง่าย
- แยก test ตามพฤติกรรมหรือ scenario เพื่อให้หาสาเหตุเมื่อ fail ได้เร็ว
- ตรวจผลด้วย assertion ที่เฉพาะเจาะจงและมีข้อความอธิบายเมื่อจำเป็น

