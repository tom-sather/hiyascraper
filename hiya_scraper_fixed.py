"""
Hiya Phone Number Scraper - FIXED VERSION
Addresses timing, URL, and element detection issues
"""

import time
import csv
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

class HiyaScraper:
    def __init__(self, headless=False):
        """Initialize the scraper with Chrome webdriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")  # Use new headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver_path = ChromeDriverManager().install()

            if not driver_path.endswith('chromedriver'):
                driver_dir = os.path.dirname(driver_path)
                for root, dirs, files in os.walk(driver_dir):
                    for file in files:
                        if file == 'chromedriver' and os.access(os.path.join(root, file), os.X_OK):
                            driver_path = os.path.join(root, file)
                            break

            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"webdriver-manager failed: {e}")
            print("Trying to use system ChromeDriver...")
            self.driver = webdriver.Chrome(options=chrome_options)

        self.wait = WebDriverWait(self.driver, 20)  # Increased timeout
        self.data = []
        self.base_domain = None  # Will be set after login

    def login(self, username, password):
        """Login to Hiya dashboard using Auth0"""
        print("Navigating to Hiya login page...")
        self.driver.get("https://app.hiya.com")

        try:
            print("Waiting for Auth0 login form...")
            time.sleep(3)

            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username'], input[type='email'], input[inputmode='email']"))
            )

            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='password'], input[type='password']")

            username_field.clear()
            username_field.send_keys(username)
            time.sleep(0.5)

            password_field.clear()
            password_field.send_keys(password)
            time.sleep(0.5)

            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button[name='action']")
            login_button.click()

            print("Waiting for dashboard to load...")
            time.sleep(8)  # Increased wait time

            current_url = self.driver.current_url
            print(f"Current URL after login: {current_url}")

            # Detect which domain we ended up on
            if "business.hiya.com" in current_url:
                self.base_domain = "business.hiya.com"
                print("✅ Detected business.hiya.com domain")
            elif "app.hiya.com" in current_url:
                self.base_domain = "app.hiya.com"
                print("✅ Detected app.hiya.com domain")
            else:
                print(f"⚠️  Unknown domain: {current_url}")
                self.base_domain = "business.hiya.com"  # Default

            if "auth-console.hiya.com" in current_url or "login" in current_url.lower():
                print("⚠️  Still on login/auth page. Please complete additional auth steps.")
            else:
                print("✅ Login successful!")

        except Exception as e:
            print(f"❌ Login error: {e}")
            raise

    def get_page_url(self, page_num):
        """Generate the URL for a specific page (0-indexed)"""
        # Try business domain first, as that's what the URL structure suggests
        if self.base_domain:
            domain = self.base_domain
        else:
            domain = "business.hiya.com"

        return f"https://{domain}/registration/cross-carrier-registration/phones?search=&status=&hasBrandedCall=&page={page_num}&size=100&sortDirection=desc&sortBy=submittedAt"

    def wait_for_page_load(self):
        """Wait for the page to fully load with multiple checks"""
        print("Waiting for page to load...")

        # Wait for initial page load
        time.sleep(3)

        # Wait for any loading spinners to disappear
        try:
            self.wait.until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='loading'], [class*='Loading'], [class*='spinner'], [class*='Spinner']"))
            )
            print("  ✓ Loading spinner disappeared")
        except TimeoutException:
            print("  ⚠ No loading spinner detected (might not exist)")

        # Wait for table or role-based structure
        try:
            self.wait.until(
                lambda d: len(d.find_elements(By.TAG_NAME, "table")) > 0 or
                         len(d.find_elements(By.CSS_SELECTOR, "[role='table']")) > 0
            )
            print("  ✓ Table structure detected")
        except TimeoutException:
            print("  ⚠ No table structure found")

        # Additional wait for content to stabilize
        time.sleep(3)

    def navigate_to_page(self, page_num):
        """Navigate directly to a specific page using URL"""
        url = self.get_page_url(page_num)
        print(f"\nNavigating to page {page_num + 1}...")
        print(f"URL: {url}")
        self.driver.get(url)

        # Wait for page to fully load
        self.wait_for_page_load()

        # Scroll to trigger any lazy loading
        print("  Scrolling to trigger lazy loading...")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        print("  ✓ Page loaded and ready")

    def get_total_pages(self):
        """Get the total number of pages from pagination"""
        try:
            # Look for "of X pages" text
            pagination_text = self.driver.find_element(By.XPATH, "//*[contains(text(), 'of') and contains(text(), 'pages')]").text
            match = re.search(r'of (\d+) pages', pagination_text)
            if match:
                total = int(match.group(1))
                print(f"📊 Found {total} total pages")
                return total
        except Exception as e:
            print(f"⚠️  Could not determine total pages from pagination: {e}")
            # Try to calculate from total records
            try:
                total_text = self.driver.find_element(By.XPATH, "//*[contains(text(), 'phone numbers')]").text
                match = re.search(r'([\d,]+)\s+phone numbers', total_text)
                if match:
                    total_records = int(match.group(1).replace(',', ''))
                    total_pages = (total_records + 99) // 100  # Ceiling division
                    print(f"📊 Calculated {total_pages} pages from {total_records} records")
                    return total_pages
            except Exception as e2:
                print(f"⚠️  Could not calculate from records: {e2}")

        return None

    def scrape_current_page(self):
        """Scrape data from the current page with improved element detection"""
        try:
            print("\n  Analyzing page structure...")

            # Check if page shows "no registered phone numbers" message
            try:
                empty_message = self.driver.find_element(By.XPATH, "//*[contains(text(), \"don't currently have any registered phone numbers\") or contains(text(), 'no registered phone numbers') or contains(text(), 'No phone numbers')]")
                if empty_message:
                    print("  📭 Found 'no registered phone numbers' message - reached end of data")
                    return -1  # Special return value to indicate we should stop
            except NoSuchElementException:
                pass  # Message not found, continue normally

            # Try to find rows using multiple methods
            rows = []
            method_used = "unknown"

            # Method 1: Standard table
            try:
                table = self.driver.find_element(By.TAG_NAME, "table")
                tbody = table.find_element(By.TAG_NAME, "tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                if rows:
                    method_used = "standard table"
                    print(f"  ✓ Found {len(rows)} rows using {method_used}")
            except:
                pass

            # Method 2: Role-based table (if method 1 failed)
            if not rows:
                try:
                    role_table = self.driver.find_element(By.CSS_SELECTOR, "[role='table']")
                    rows = role_table.find_elements(By.CSS_SELECTOR, "[role='row']")
                    # Filter out header rows
                    rows = [r for r in rows if r.find_elements(By.CSS_SELECTOR, "[role='cell']")]
                    if rows:
                        method_used = "role-based table"
                        print(f"  ✓ Found {len(rows)} rows using {method_used}")
                except:
                    pass

            if not rows:
                print("  ❌ No rows found on this page")
                # Save debug info
                self.save_debug_info()
                return 0

            page_count = 0
            skipped = 0

            # Extract data from each row
            for idx, row in enumerate(rows):
                try:
                    # Re-find the row to avoid stale element issues
                    if method_used == "standard table":
                        table = self.driver.find_element(By.TAG_NAME, "table")
                        tbody = table.find_element(By.TAG_NAME, "tbody")
                        current_rows = tbody.find_elements(By.TAG_NAME, "tr")
                        if idx >= len(current_rows):
                            continue
                        row = current_rows[idx]
                        cells = row.find_elements(By.TAG_NAME, "td")
                    else:
                        role_table = self.driver.find_element(By.CSS_SELECTOR, "[role='table']")
                        current_rows = role_table.find_elements(By.CSS_SELECTOR, "[role='row']")
                        current_rows = [r for r in current_rows if r.find_elements(By.CSS_SELECTOR, "[role='cell']")]
                        if idx >= len(current_rows):
                            continue
                        row = current_rows[idx]
                        cells = row.find_elements(By.CSS_SELECTOR, "[role='cell']")

                    if len(cells) < 5:
                        skipped += 1
                        continue

                    # Column mapping:
                    # [0] = checkbox
                    # [1] = Phone number
                    # [2] = Submitted (date + email)
                    # [3] = Registration job name
                    # [4] = Branded Call
                    # [5] = Spam labeling
                    # [6] = Spam category
                    # [7+] = Registration status

                    phone_number = cells[1].text.strip() if len(cells) > 1 else ""

                    # Skip header rows or empty rows
                    if not phone_number or phone_number == "Phone number" or phone_number == "":
                        skipped += 1
                        continue

                    submitted_cell_text = cells[2].text.strip() if len(cells) > 2 else ""
                    lines = submitted_cell_text.split('\n')
                    submitted_date = lines[0] if len(lines) > 0 else ""
                    submitted_email = lines[1] if len(lines) > 1 else ""

                    registration_job = cells[3].text.strip() if len(cells) > 3 else ""
                    branded_call = cells[4].text.strip() if len(cells) > 4 else ""
                    spam_labeling = cells[5].text.strip() if len(cells) > 5 else ""
                    spam_category = cells[6].text.strip() if len(cells) > 6 else ""
                    registration_status = cells[7].text.strip() if len(cells) > 7 else ""

                    record = {
                        'phone_number': phone_number,
                        'submitted_date': submitted_date,
                        'submitted_by': submitted_email,
                        'registration_job_name': registration_job,
                        'branded_call': branded_call,
                        'spam_labeling': spam_labeling,
                        'spam_category': spam_category,
                        'registration_status': registration_status
                    }

                    self.data.append(record)
                    page_count += 1

                except StaleElementReferenceException:
                    print(f"    ⚠ Stale element at row {idx}, retrying...")
                    continue
                except Exception as e:
                    print(f"    ⚠ Error parsing row {idx}: {e}")
                    continue

            print(f"  ✓ Extracted {page_count} records (skipped {skipped} rows)")
            return page_count

        except Exception as e:
            print(f"  ❌ Error scraping page: {e}")
            import traceback
            traceback.print_exc()
            self.save_debug_info()
            return 0

    def save_debug_info(self):
        """Save debug information when scraping fails"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Save page source
            with open(f'debug_page_source_{timestamp}.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)

            # Save screenshot
            self.driver.save_screenshot(f'debug_screenshot_{timestamp}.png')

            print(f"  💾 Debug files saved with timestamp: {timestamp}")
        except Exception as e:
            print(f"  ⚠ Could not save debug info: {e}")

    def scrape_all_pages(self, max_pages=None):
        """Scrape all pages by navigating directly via URL"""
        print("\n" + "="*60)
        print("STARTING TO SCRAPE ALL PAGES")
        print("="*60)

        # First, go to page 0 to get total pages
        self.navigate_to_page(0)
        total_pages = self.get_total_pages()

        if not total_pages:
            print("⚠️  Could not determine total pages. Will scrape until empty page.")
            total_pages = max_pages if max_pages else 50

        if max_pages and max_pages < total_pages:
            total_pages = max_pages
            print(f"ℹ️  Limiting to {max_pages} pages as requested")

        # Start scraping from page 0
        empty_pages = 0
        for page_num in range(total_pages):
            print(f"\n{'='*60}")
            print(f"PAGE {page_num + 1} of {total_pages}")
            print(f"{'='*60}")

            # Navigate to this page (skip if we're already on page 0)
            if page_num > 0:
                self.navigate_to_page(page_num)

            # Scrape the page
            count = self.scrape_current_page()

            # Check if we hit the empty page message
            if count == -1:
                print("✅ Reached end of data (empty page message found)")
                break

            if count == 0:
                print("⚠️  No records found on this page")
                empty_pages += 1
                # If we get 2 empty pages in a row, stop
                if empty_pages >= 2:
                    print("⚠️  Two consecutive empty pages. Stopping.")
                    break
                continue
            else:
                empty_pages = 0  # Reset counter

            print(f"✅ Scraped {count} records from page {page_num + 1}")
            print(f"📊 Total records so far: {len(self.data)}")

        print(f"\n{'='*60}")
        print(f"SCRAPING COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Total records scraped: {len(self.data)}")

    def save_to_csv(self, filename=None):
        """Save scraped data to CSV file"""
        if not filename:
            filename = f"hiya_phone_numbers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        if not self.data:
            print("❌ No data to save!")
            return None

        print(f"\n💾 Saving data to {filename}...")

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = self.data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(self.data)

        print(f"✅ Successfully saved {len(self.data)} records to {filename}")
        return filename

    def close(self):
        """Close the browser"""
        self.driver.quit()
        print("Browser closed")


def main():
    """Main function to run the scraper"""

    print("="*60)
    print("Hiya Phone Number Scraper - FIXED VERSION")
    print("="*60)
    print("\nFixes applied:")
    print("  • Dynamic domain detection")
    print("  • Improved wait times for dynamic content")
    print("  • Better element detection")
    print("  • Stale element handling")
    print("  • Debug file generation on errors")
    print("\n")

    username = input("Enter your Hiya username/email: ")
    password = input("Enter your Hiya password: ")

    scraper = HiyaScraper(headless=False)

    try:
        # Login
        scraper.login(username, password)

        # Handle 2FA if needed
        print("\n🔐 If you have 2FA enabled, please complete it now...")
        print("Press Enter once you're logged in and ready to continue...")
        input()

        # Scrape all pages
        scraper.scrape_all_pages()

        # Save to CSV
        if scraper.data:
            filename = scraper.save_to_csv()
            print(f"\n🎉 SUCCESS! Your data is saved to: {filename}")
            print(f"📊 Total records: {len(scraper.data)}")
        else:
            print("\n⚠️  No data was scraped.")
            print("Check the debug files (debug_page_source_*.html and debug_screenshot_*.png) for more info.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        if scraper.data:
            print("💾 Saving partial data...")
            scraper.save_to_csv()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

        if scraper.data:
            print("\n💾 Saving partial data...")
            scraper.save_to_csv()

    finally:
        print("\nClosing browser in 3 seconds...")
        time.sleep(3)
        scraper.close()


if __name__ == "__main__":
    main()
