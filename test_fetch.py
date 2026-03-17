from playwright.sync_api import sync_playwright

def test_pmc(page):
    page.goto("http://127.0.0.1:8001")
    page.click("#minePmcBtn")
    page.wait_for_timeout(3000)

    val = page.locator("#inputText").input_value()
    print("Input Text:", val[:100])

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_pmc(page)
        finally:
            browser.close()
