from playwright.sync_api import sync_playwright
import re
import sys

URL = "https://svoy-narcolog.ru/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle", timeout=60000)

    # open consult modal
    open_btn = page.locator('[data-modal-open="consult"]').first
    open_btn.click()
    page.wait_for_selector('[data-modal="consult"]:not([hidden])', timeout=10000)

    # fill form
    page.fill("#consult-name", "тест")
    phone = page.locator("#consult-phone")
    phone.click()
    phone.type("9034110003", delay=40)
    phone_value = phone.input_value()
    print("PHONE_MASKED:", phone_value)
    if not re.match(r"^\+7 \(903\) 411-00-03$", phone_value):
        print("MASK_FAIL")
        browser.close()
        sys.exit(1)

    page.fill("#consult-message", "тестовая заявка")

    with page.expect_response(lambda r: "/send.php" in r.url and r.request.method == "POST", timeout=30000) as resp_info:
        page.locator('[data-consult-form] button[type="submit"]').click()

    resp = resp_info.value
    body = resp.text()
    print("STATUS:", resp.status)
    print("BODY:", body)

    page.wait_for_selector(".consult-form__status--success", timeout=15000)
    status_text = page.locator("[data-consult-status]").inner_text()
    print("UI_STATUS:", status_text)

    browser.close()
    if resp.status != 200 or '"ok":true' not in body.replace(" ", ""):
        # allow spaced JSON
        if '"ok": true' not in body and '"ok":true' not in body:
            sys.exit(2)
    print("FORM_OK")
