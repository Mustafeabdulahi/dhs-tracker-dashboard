#!/usr/bin/env python3
"""
DHS Worst of the Worst - Enhanced Scraper with Historical Tracking
Tracks when people first appear on the database
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class DHSDatabase:
    """Manages historical tracking of DHS arrests"""

    def __init__(self, db_path: str = "data/historical_arrests.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load_database()

    def _load_database(self) -> Dict:
        """Load existing database"""
        if self.db_path.exists():
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"records": {}, "metadata": {"last_updated": None, "total_scrapes": 0}}

    def _save_database(self):
        """Save database to disk"""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.data, indent=2, fp=f, ensure_ascii=False)

    def update_records(self, new_records: List[Dict], min_expected_records: int = 100) -> Dict:
        """
        Update database with new scrape results
        Returns statistics about changes
        
        Args:
            new_records: List of newly scraped records
            min_expected_records: Minimum records expected for a successful scrape.
                                 If less, don't mark missing records as removed.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        stats = {
            "new_people": [],
            "updated_people": [],
            "still_present": 0,
            "total_in_scrape": len(new_records),
        }

        # Safety check: if we got very few records, something went wrong
        current_active = sum(1 for r in self.data["records"].values() if r["status"] == "active")
        scrape_looks_incomplete = len(new_records) < min_expected_records
        
        if scrape_looks_incomplete and current_active > len(new_records) * 2:
            print(f"\n⚠️  WARNING: Scraped only {len(new_records)} records but have {current_active} active.")
            print(f"⚠️  This looks like an incomplete scrape. Will NOT mark missing records as removed.")
            print(f"⚠️  Set min_expected_records lower if this is intentional.\n")

        # Create a set of names from new scrape
        scraped_names = {r["name"] for r in new_records}

        # Update existing records and add new ones
        for record in new_records:
            name = record["name"]

            if name not in self.data["records"]:
                # NEW PERSON - first time seeing them
                record["first_seen_date"] = today
                record["last_seen_date"] = today
                record["status"] = "active"
                record["scrape_count"] = 1
                self.data["records"][name] = record
                stats["new_people"].append(name)
                print(f"  🆕 NEW: {name}")
            else:
                # EXISTING PERSON - update last seen
                existing = self.data["records"][name]

                # Check if any data changed
                data_changed = False
                for key in [
                    "country",
                    "convicted_of",
                    "arrested_location",
                    "image_url",
                ]:
                    if key in record and record[key] != existing.get(key):
                        data_changed = True
                        break

                if data_changed:
                    stats["updated_people"].append(name)

                # Update record
                existing["last_seen_date"] = today
                existing["scrape_count"] = existing.get("scrape_count", 0) + 1

                # Update any changed fields
                for key, value in record.items():
                    if key not in [
                        "first_seen_date",
                        "last_seen_date",
                        "status",
                        "scrape_count",
                    ]:
                        existing[key] = value

                stats["still_present"] += 1

        # Mark people who are no longer in the database
        # BUT ONLY if the scrape looks complete
        if not scrape_looks_incomplete:
            for name, record in self.data["records"].items():
                if name not in scraped_names and record["status"] == "active":
                    record["status"] = "removed"
                    record["removed_date"] = today
                    print(f"  ❌ REMOVED: {name}")
        else:
            print(f"\n✓ Skipped marking missing records as removed (scrape appears incomplete)")

        # Update metadata
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        self.data["metadata"]["total_scrapes"] = (
            self.data["metadata"].get("total_scrapes", 0) + 1
        )
        self.data["metadata"]["total_records"] = len(self.data["records"])
        self.data["metadata"]["active_records"] = sum(
            1 for r in self.data["records"].values() if r["status"] == "active"
        )

        self._save_database()
        return stats

    def search_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Find people who first appeared between two dates"""
        results = []
        for record in self.data["records"].values():
            first_seen = record["first_seen_date"]
            if start_date <= first_seen <= end_date:
                results.append(record)
        return results

    def search_by_name(self, query: str) -> List[Dict]:
        """Fuzzy search by name"""
        query = query.lower()
        results = []
        for record in self.data["records"].values():
            if query in record["name"].lower():
                results.append(record)
        return results

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        records = list(self.data["records"].values())
        active = [r for r in records if r["status"] == "active"]

        # Count by country
        country_counts = {}
        for r in active:
            country = r.get("country", "Unknown")
            country_counts[country] = country_counts.get(country, 0) + 1

        # Count by state
        state_counts = {}
        for r in active:
            location = r.get("arrested_location", "")
            # Extract state from "City, State" format
            if "," in location:
                state = location.split(",")[-1].strip()
                state_counts[state] = state_counts.get(state, 0) + 1

        return {
            "total_records": len(records),
            "active_records": len(active),
            "removed_records": len(records) - len(active),
            "top_countries": sorted(
                country_counts.items(), key=lambda x: x[1], reverse=True
            )[:10],
            "top_states": sorted(
                state_counts.items(), key=lambda x: x[1], reverse=True
            )[:10],
            "last_updated": self.data["metadata"].get("last_updated"),
            "total_scrapes": self.data["metadata"].get("total_scrapes", 0),
        }


class DHSWoWScraper:
    """Selenium-based scraper for DHS Worst of the Worst"""

    def __init__(self, headless: bool = True, delay: float = 2.0):
        self.headless = headless
        self.delay = delay
        self.driver = None
        self.base_url = "https://www.dhs.gov/wow"

    def setup_driver(self):
        """Setup Chrome WebDriver"""
        print("Setting up Chrome WebDriver...")

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            print("✓ WebDriver initialized\n")
            return True
        except Exception as e:
            print(f"✗ Error initializing WebDriver: {e}")
            return False

    def load_page(self, url: str = None) -> bool:
        """Load the main page"""
        try:
            url = url or self.base_url
            self.driver.get(url)
            time.sleep(self.delay + 1)
            return True
        except Exception as e:
            print(f"✗ Error loading page: {e}")
            return False

    def extract_all_cards(self) -> List[Dict]:
        """Extract all person cards from current page"""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.usa-card"))
            )
            time.sleep(3)

            cards = self.driver.find_elements(By.CSS_SELECTOR, "li.usa-card")
            if not cards:
                return []

            records = []
            for idx, card in enumerate(cards, 1):
                try:
                    full_text = card.text.strip()
                    if not full_text or len(full_text) < 20:
                        continue

                    record = {}
                    lines = full_text.split("\n")

                    # Extract country (first line, all caps)
                    if lines and lines[0].isupper() and len(lines[0]) < 30:
                        record["country"] = lines[0].strip()

                    # Find section markers
                    convicted_idx = next(
                        (
                            i
                            for i, line in enumerate(lines)
                            if "CONVICTED OF:" in line.upper()
                            or "ARRESTED FOR:" in line.upper()
                        ),
                        None,
                    )
                    arrested_idx = next(
                        (
                            i
                            for i, line in enumerate(lines)
                            if line.strip().upper() == "ARRESTED:"
                        ),
                        None,
                    )
                    name_idx = next(
                        (
                            i
                            for i, line in enumerate(lines)
                            if line.strip().upper() == "NAME:"
                        ),
                        None,
                    )

                    # Extract convicted_of
                    if convicted_idx is not None and arrested_idx is not None:
                        crime_lines = lines[convicted_idx + 1 : arrested_idx]
                        crime_text = " ".join(
                            [l.strip() for l in crime_lines if l.strip()]
                        )
                        if crime_text:
                            record["convicted_of"] = crime_text

                    # Extract location
                    if arrested_idx is not None and name_idx is not None:
                        location_lines = lines[arrested_idx + 1 : name_idx]
                        location_text = " ".join(
                            [l.strip() for l in location_lines if l.strip()]
                        )
                        if location_text:
                            record["arrested_location"] = location_text

                    # Extract name
                    if name_idx is not None and name_idx + 1 < len(lines):
                        name_lines = lines[name_idx + 1 :]
                        name_parts = []
                        for line in name_lines:
                            line = line.strip()
                            if line == ">>" or not line:
                                break
                            name_parts.append(line)
                        name_text = " ".join(name_parts)
                        if name_text:
                            record["name"] = name_text

                    # Extract image URL
                    try:
                        img = card.find_element(By.CSS_SELECTOR, "img")
                        src = img.get_attribute("src")
                        if src:
                            if src.startswith("/"):
                                src = "https://www.dhs.gov" + src
                            record["image_url"] = src
                    except:
                        pass

                    # Extract press release URL
                    try:
                        press_link = card.find_element(
                            By.CSS_SELECTOR, "a.usa-card__more"
                        )
                        href = press_link.get_attribute("href")
                        if href:
                            if href.startswith("/"):
                                href = "https://www.dhs.gov" + href
                            record["press_release_url"] = href
                    except:
                        pass

                    if record.get("name"):
                        records.append(record)

                except Exception as e:
                    continue

            return records

        except Exception as e:
            print(f"  ✗ Error extracting cards: {e}")
            return []

    def load_page_number(self, page_index: int) -> bool:
        """
        Navigate directly to a page by index (0-based) using the ?page=X query param.
        This avoids brittle Next-button clicking and ensures we can jump to deep pages.
        """
        try:
            if page_index <= 0:
                url = self.base_url
            else:
                url = f"{self.base_url}?page={page_index}"
            self.driver.get(url)
            time.sleep(self.delay + 1)
            return True
        except Exception as e:
            print(f"  ⚠️  Error loading page index {page_index}: {e}")
            return False

    def get_cards_with_retry(self, page_index: int, attempts: int = 2) -> List[Dict]:
        """
        Load a page and extract cards, with retry and scroll to handle lazy loading.
        """
        for attempt in range(1, attempts + 1):
            if not self.load_page_number(page_index):
                continue

            # Nudge the page to load lazy content
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            except Exception:
                pass
            time.sleep(self.delay + 1)

            cards = self.extract_all_cards()
            if cards:
                return cards

            print(f"  ⚠️  No cards found on page {page_index+1}, retry {attempt}/{attempts}")
            time.sleep(self.delay + 2)

        return []

    def apply_filters(
        self, country: str = None, state: str = None, search_term: str = None
    ):
        """Apply filters on the page"""
        try:
            if search_term:
                search_input = self.driver.find_element(By.ID, "edit-combine")
                search_input.clear()
                search_input.send_keys(search_term)

            if country:
                try:
                    country_select = Select(
                        self.driver.find_element(
                            By.ID, "edit-field-country-of-origin-target-id"
                        )
                    )
                    country_select.select_by_visible_text(country)
                except:
                    pass

            if state:
                try:
                    state_select = Select(
                        self.driver.find_element(By.ID, "edit-field-state-value")
                    )
                    state_select.select_by_visible_text(state)
                except:
                    pass

            try:
                search_button = self.driver.find_element(By.ID, "edit-submit-wow")
                search_button.click()
                time.sleep(self.delay + 1)
            except:
                pass
        except Exception as e:
            print(f"  Error applying filters: {e}")

    def scrape_all(
        self,
        country: str = None,
        state: str = None,
        max_pages: int = 50,
        max_results: int = None,
    ) -> List[Dict]:
        """
        Scrape all records using direct page navigation (?page=N) to avoid flaky clicks.
        Pages on DHS are 0-based in the query param; UI shows 1-based.
        """
        all_records = []

        if not self.setup_driver():
            return all_records

        if country or state:
            # Load first page and apply filters once
            if not self.load_page_number(0):
                return all_records
            self.apply_filters(country=country, state=state)
            time.sleep(self.delay)
        else:
            # Ensure first page is loaded
            if not self.load_page_number(0):
                return all_records

        consecutive_empty = 0

        for page_num in range(1, max_pages + 1):
            page_index = page_num - 1  # zero-based for the ?page= param
            print(f"Page {page_num} (page param={page_index})...", end=" ")

            cards = self.get_cards_with_retry(page_index, attempts=2)

            if cards:
                all_records.extend(cards)
                print(f"✓ {len(cards)} records (Total: {len(all_records)})")
                consecutive_empty = 0

                if max_results and len(all_records) >= max_results:
                    all_records = all_records[:max_results]
                    break
            else:
                consecutive_empty += 1
                print(f"✗ Empty (attempt {consecutive_empty}/3)")
                if consecutive_empty >= 3:
                    print("\n⚠️  Three consecutive empty pages, stopping scrape")
                    break

        print(f"\n{'='*70}")
        print(f"Scraping completed: {len(all_records)} total records from {page_num} pages")
        print(f"{'='*70}\n")
        return all_records

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()


def main():
    """Main scraping function with database tracking"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scrape DHS Worst of the Worst with historical tracking"
    )
    parser.add_argument("--country", type=str, help="Filter by country")
    parser.add_argument("--state", type=str, help="Filter by state")
    parser.add_argument("--max-pages", type=int, default=50, help="Max pages")
    parser.add_argument("--max-results", type=int, help="Max total results")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay in seconds")
    parser.add_argument("--visible", action="store_true", help="Show browser")
    parser.add_argument("--export-csv", action="store_true", help="Export to CSV")
    parser.add_argument(
        "--min-expected-records",
        type=int,
        default=100,
        help="If scrape returns fewer than this, skip marking records removed.",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("DHS WORST OF THE WORST - HISTORICAL TRACKER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'Visible' if args.visible else 'Headless'}")
    if args.country:
        print(f"Filter: Country = {args.country}")
    if args.state:
        print(f"Filter: State = {args.state}")
    print("=" * 70 + "\n")

    # Initialize scraper
    scraper = DHSWoWScraper(headless=not args.visible, delay=args.delay)

    if not scraper.setup_driver():
        return

    try:
        # Scrape data
        print("Starting scrape...\n")
        records = scraper.scrape_all(
            country=args.country,
            state=args.state,
            max_pages=args.max_pages,
            max_results=args.max_results,
        )

        print(f"\n{'=' * 70}")
        print(f"SCRAPING COMPLETE: {len(records)} records")
        print(f"{'=' * 70}\n")

        if records:
            # Update database
            print("Updating historical database...")
            db = DHSDatabase()
            stats = db.update_records(records, min_expected_records=args.min_expected_records)

            print(f"\n{'=' * 70}")
            print("DATABASE UPDATE SUMMARY")
            print(f"{'=' * 70}")
            print(f"New people added: {len(stats['new_people'])}")
            print(f"Updated records: {len(stats['updated_people'])}")
            print(f"Still present: {stats['still_present']}")
            print(f"Total in scrape: {stats['total_in_scrape']}")

            if stats["new_people"]:
                print(f"\n🆕 NEW ARRIVALS ({len(stats['new_people'])}):")
                for name in stats["new_people"][:10]:
                    print(f"   • {name}")
                if len(stats["new_people"]) > 10:
                    print(f"   ... and {len(stats['new_people']) - 10} more")

            # Get overall statistics
            db_stats = db.get_statistics()
            print(f"\n{'=' * 70}")
            print("DATABASE STATISTICS")
            print(f"{'=' * 70}")
            print(f"Total records: {db_stats['total_records']}")
            print(f"Active records: {db_stats['active_records']}")
            print(f"Removed records: {db_stats['removed_records']}")
            print(f"Total scrapes: {db_stats['total_scrapes']}")

            print(f"\nTop 5 Countries:")
            for country, count in db_stats["top_countries"][:5]:
                print(f"   {country}: {count}")

            print(f"\nTop 5 States:")
            for state, count in db_stats["top_states"][:5]:
                print(f"   {state}: {count}")

            # Export CSV if requested
            if args.export_csv:
                import csv

                csv_file = f"data/export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                Path(csv_file).parent.mkdir(parents=True, exist_ok=True)

                with open(csv_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=[
                            "name",
                            "country",
                            "convicted_of",
                            "arrested_location",
                            "first_seen_date",
                            "last_seen_date",
                            "status",
                        ],
                    )
                    writer.writeheader()
                    for record in db.data["records"].values():
                        writer.writerow(
                            {k: record.get(k, "") for k in writer.fieldnames}
                        )

                print(f"\n✓ Exported to: {csv_file}")
        else:
            print("\n✗ No records scraped")

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
