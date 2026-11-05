# Lab 05 — Playwright กับ Python และ pytest

คู่มือสร้าง browser test ด้วย Playwright Python และ pytest ตั้งแต่เริ่มต้น อธิบายแนวคิดของ fixture, locator, action และ assertion โดยไม่ผูกกับโจทย์ของเว็บใด

## สิ่งที่ต้องมี

- Python 3.14 (โปรเจกต์นี้กำหนด `requires-python = ">=3.14"`)
- `uv`
- Browser ที่ Playwright รองรับ (ติดตั้งผ่านคำสั่ง Playwright ด้านล่าง)

ติดตั้ง `uv` ตามเอกสารทางการ แล้วตรวจสอบด้วย `python --version` และ `uv --version`

## สร้างโปรเจกต์จากศูนย์

```cmd
uv init --package --python 3.14 playwright-python-tests
cd /d playwright-python-tests
uv add --dev pytest pytest-playwright
uv run playwright install chromium
mkdir tests
```

`pytest-playwright` ให้ fixture เช่น `page` สำหรับแต่ละ browser test ส่วนคำสั่ง `playwright install` จะติดตั้ง browser binary ที่ Playwright ใช้ทดสอบ หากต้องการติดตั้ง browser ที่รองรับหลายตัว ให้ใช้ `uv run playwright install` โดยไม่ระบุชื่อ browser.

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

```cmd
uv sync
uv run playwright install chromium
uv run pytest
```

รัน test เฉพาะไฟล์หรือเลือก test ได้ด้วย:

```cmd
uv run pytest tests/test_smoke.py -v
uv run pytest -k sorting -v
```

เมื่อรันผ่าน Playwright pytest plugin จะเปิด browser แบบ headless ตามปกติ หากต้องการเห็น browser ให้ใช้ `--headed`:

```cmd
uv run pytest --headed
```

## แนวทางที่ควรทำ

- เลือก locator ที่สื่อความหมายและทนต่อการเปลี่ยน layout เช่น role/label หรือ `data-test`
- ใช้ fixture แบ่ง setup และ cleanup ให้ test อ่านง่าย
- แยก test ตามพฤติกรรมหรือ scenario เพื่อให้หาสาเหตุเมื่อ fail ได้เร็ว
- ตรวจผลด้วย assertion ที่เฉพาะเจาะจงและมีข้อความอธิบายเมื่อจำเป็น



## เปิดดูระหว่างสอบ: ทางลัดและภาพรวมไฟล์นี้

เริ่มจาก `def test_...(page):` ใช้ fixture `page`, เปิด URL ด้วย `page.goto()`, หา element ด้วย locator, ทำ action แล้วตรวจผลด้วย `assert` หรือ Playwright `expect`. `tests/conftest.py` เหมาะกับ fixture ที่ใช้ซ้ำ เช่น เตรียมหน้าให้พร้อมก่อนหลาย test. ใช้ locator แบบ role/label/test id เมื่อมีให้เลือก

ไฟล์ทดสอบปัจจุบัน:

| ไฟล์ | สิ่งที่แสดงให้ดู |
|---|---|
| `test_smoke.py` | ทดสอบ login สำเร็จและตรวจ URL/title |
| `test_sorting.py` | เลือกการเรียงราคา อ่านค่าหลาย element แล้ว assert ลำดับ |
| `test_checkout_flow.py` | ทำ flow ตั้งแต่เลือกสินค้า ตรวจราคารวม ภาษี และผลสำเร็จ |
| `test_playwright.py` | รวมตัวอย่าง login, sorting และ checkout ไว้ในไฟล์เดียว เนื้อหาบางส่วนซ้ำกับไฟล์แยกด้านบน |

### คำสั่งที่ใช้บ่อย

```cmd
uv sync
uv run playwright install chromium
uv run pytest -v
uv run pytest tests/test_sorting.py -v
uv run pytest --headed                       # เปิด browser ให้เห็น
uv run pytest -k sorting -v                   # เลือก test จากชื่อ
```

### เมื่อเจอปัญหา

- ไม่มี browser executable: รัน `uv run playwright install chromium`
- fixture `page` ไม่รู้จัก: ตรวจว่าติดตั้ง `pytest-playwright` ใน environment นี้แล้ว
- locator จับหลาย element/ไม่เจอ: ใช้ locator ที่เฉพาะเจาะจงขึ้นและตรวจหน้า/สถานะปัจจุบัน
- test fail ชั่วคราว: ใช้ `--headed` หรือ `PWDEBUG=1` เพื่อดูการทำงานทีละขั้น

### เอกสารอ้างอิงขณะสอบ

- [Playwright Python: Writing tests](https://playwright.dev/python/docs/writing-tests)
- [Playwright Python: Locators](https://playwright.dev/python/docs/locators)
- [Playwright Python: Assertions](https://playwright.dev/python/docs/test-assertions)
- [Playwright Python: Running and debugging tests](https://playwright.dev/python/docs/running-tests)
- [uv: Working on projects](https://docs.astral.sh/uv/guides/projects/)

