#!/usr/bin/env python3
"""
Ad-hoc tester for specific DHS WOW pages.

Usage examples:
  python test.py --pages 208,209,210 --visible
  python test.py --pages 208,209,210 --headless

Notes:
- UI page numbers are 1-based. The underlying query param is 0-based, so we
  subtract 1 when building the URL (?page=N).
- This script only probes the specified pages, logs card counts, and reports
  extraction errors to help debug pagination issues (e.g., pages 208–210).
"""

import argparse
import sys
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://www.dhs.gov/wow"


def setup_driver(headless: bool = True, delay: float = 2.0):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=opts)
    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    except Exception:
        pass

    # small settle time
    time.sleep(delay)
    return driver


def load_page(driver, page_ui: int, delay: float):
    page_param = max(page_ui - 1, 0)  # convert to 0-based
    url = f"{BASE_URL}?page={page_param}" if page_param > 0 else BASE_URL
    print(f"\n=== Loading page {page_ui} (param={page_param}) -> {url}")
    driver.get(url)
    time.sleep(delay + 1)

    # Light scroll to encourage lazy loading
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    except Exception:
        pass
    time.sleep(delay)


def extract_cards(driver, timeout: float = 10.0) -> List:
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.usa-card"))
        )
    except Exception as e:
        print(f"  ⚠️  Timeout waiting for cards: {e}")
        return []

    try:
        cards = driver.find_elements(By.CSS_SELECTOR, "li.usa-card")
        return cards
    except Exception as e:
        print(f"  ✗ Error locating cards: {e}")
        return []


def test_pages(pages: List[int], headless: bool, delay: float):
    driver = None
    try:
        driver = setup_driver(headless=headless, delay=delay)
        for p in pages:
            load_page(driver, p, delay)
            cards = extract_cards(driver, timeout=12.0)
            if cards:
                print(f"  ✓ Found {len(cards)} cards on page {p}")
            else:
                print(f"  ✗ No cards found on page {p}")
    finally:
        if driver:
            driver.quit()


def parse_pages(arg: str) -> List[int]:
    try:
        return [int(x.strip()) for x in arg.split(",") if x.strip()]
    except ValueError:
        print("Invalid --pages value. Use comma-separated integers, e.g., 208,209,210.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Probe specific DHS WOW pages for card extraction issues."
    )
    parser.add_argument(
        "--pages",
        type=str,
        default="208,209,210",
        help="Comma-separated UI page numbers to test (1-based).",
    )
    parser.add_argument(
        "--visible", action="store_true", help="Show browser (disables headless)."
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Base delay between steps (seconds).",
    )
    args = parser.parse_args()

    pages = parse_pages(args.pages)
    headless = not args.visible

    print(
        f"Testing pages: {pages} | headless={headless} | delay={args.delay:.1f}s\n"
        "UI pages are 1-based; query param is 0-based (?page=N)."
    )
    test_pages(pages, headless=headless, delay=args.delay)


if __name__ == "__main__":
    main()
