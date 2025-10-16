"""
Hiya Phone Number Scraper - DEBUG VERSION
This version will help us inspect the page and figure out the correct selectors
"""

import time
import csv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class HiyaScraperDebug:
    def __init__(self, headless=False):
        """Initialize the scraper with Chrome webdriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Try to use webdriver-manager, but fall back to system chromedriver if needed
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver_path = ChromeDriverManager().install()
            
            # Fix for Mac ARM: webdriver-manager sometimes returns wrong file path
            if not driver_path.endswith('chromedriver'):
                driver_dir = os.path.dirname(driver_path)
                # Look for the actual chromedriver executable
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
        
        self.wait = WebDriverWait(self.driver, 10)
        self.data = []
        
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
            print("Found username field")
            
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='password'], input[type='password']")
            print("Found password field")
            
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(0.5)
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button[name='action']")
            print("Clicking login button...")
            login_button.click()
            
            print("Waiting for dashboard to load...")
            time.sleep(5)
            
            current_url = self.driver.current_url
            print(f"Current URL after login: {current_url}")
            
            if "auth-console.hiya.com" in current_url or "login" in current_url.lower():
                print("⚠️  Still on login/auth page.")
                print("Please complete any additional authentication steps manually.")
            else:
                print("✅ Login successful!")
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def navigate_to_phone_numbers(self):
        """Navigate to the Phone numbers page"""
        print("\n" + "="*60)
        print("NAVIGATION STEP")
        print("="*60)
        
        time.sleep(2)
        current_url = self.driver.current_url
        print(f"Current URL: {current_url}")
        
        if "phone" in current_url.lower() or "registration" in current_url.lower():
            print("Already on Phone numbers page")
            return
        
        print("\nNavigating directly to phone numbers page...")
        self.driver.get("https://app.hiya.com/number-registration/phone-numbers")
        time.sleep(4)
        
        current_url = self.driver.current_url
        print(f"New URL: {current_url}")
        
        if "phone" in current_url.lower() or "registration" in current_url.lower():
            print("✅ Successfully navigated to Phone numbers page")
        else:
            print("⚠️  URL doesn't contain expected keywords")
    
    def inspect_page(self):
        """Inspect the page structure to find the data table"""
        print("\n" + "="*60)
        print("PAGE INSPECTION")
        print("="*60)
        
        # Save page source for manual inspection
        page_source = self.driver.page_source
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("✅ Saved page source to 'page_source.html'")
        
        # Save screenshot
        self.driver.save_screenshot('page_screenshot.png')
        print("✅ Saved screenshot to 'page_screenshot.png'")
        
        # Look for tables
        print("\n--- Looking for tables ---")
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} <table> elements")
        
        # Look for elements with role="table"
        role_tables = self.driver.find_elements(By.CSS_SELECTOR, "[role='table']")
        print(f"Found {len(role_tables)} elements with role='table'")
        
        # Look for common table classes
        common_classes = [
            ".MuiTable-root",
            ".ant-table",
            ".data-table",
            "[class*='table']",
            "[class*='Table']",
        ]
        
        for class_selector in common_classes:
            elements = self.driver.find_elements(By.CSS_SELECTOR, class_selector)
            if elements:
                print(f"Found {len(elements)} elements matching: {class_selector}")
        
        # Look for tbody and rows
        print("\n--- Looking for rows ---")
        tbody = self.driver.find_elements(By.TAG_NAME, "tbody")
        print(f"Found {len(tbody)} <tbody> elements")
        
        tr_elements = self.driver.find_elements(By.TAG_NAME, "tr")
        print(f"Found {len(tr_elements)} <tr> elements")
        
        role_rows = self.driver.find_elements(By.CSS_SELECTOR, "[role='row']")
        print(f"Found {len(role_rows)} elements with role='row'")
        
        # Try to find the phone number text
        print("\n--- Looking for phone numbers ---")
        try:
            # Look for the first phone number from your screenshot: +1 213 731 2373
            phone_xpath = "//*[contains(text(), '+1 213 731 2373')]"
            phone_element = self.driver.find_element(By.XPATH, phone_xpath)
            print(f"✅ Found phone number element!")
            print(f"   Tag: {phone_element.tag_name}")
            print(f"   Class: {phone_element.get_attribute('class')}")
            print(f"   Text: {phone_element.text}")
            
            # Get parent element
            parent = phone_element.find_element(By.XPATH, "..")
            print(f"\n   Parent tag: {parent.tag_name}")
            print(f"   Parent class: {parent.get_attribute('class')}")
            
        except NoSuchElementException:
            print("❌ Could not find the specific phone number")
            print("   Trying to find any phone-like pattern...")
            
            # Try regex-like search
            all_text = self.driver.find_element(By.TAG_NAME, "body").text
            if "+1" in all_text:
                print("   ✅ Found '+1' in page text")
                lines_with_phones = [line for line in all_text.split('\n') if '+1' in line]
                print(f"   Found {len(lines_with_phones)} lines with '+1'")
                if lines_with_phones:
                    print(f"   First few lines: {lines_with_phones[:3]}")
            else:
                print("   ❌ No '+1' found in page text")
        
        # Look for pagination info
        print("\n--- Looking for pagination ---")
        try:
            pagination_text = self.driver.find_element(By.XPATH, "//*[contains(text(), '1,331') or contains(text(), 'phone numbers')]")
            print(f"✅ Found pagination text: {pagination_text.text}")
        except:
            print("❌ Could not find pagination info")
    
    def try_scraping_methods(self):
        """Try different methods to scrape the data"""
        print("\n" + "="*60)
        print("TRYING DIFFERENT SCRAPING METHODS")
        print("="*60)
        
        methods_tried = []
        
        # Method 1: Standard table
        print("\n--- Method 1: Standard HTML table ---")
        try:
            table = self.driver.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            print(f"✅ Found {len(rows)} rows in table")
            
            if rows:
                first_row = rows[0]
                cells = first_row.find_elements(By.TAG_NAME, "td")
                print(f"   First row has {len(cells)} cells")
                print(f"   Cell contents: {[cell.text for cell in cells[:5]]}")
                methods_tried.append(("Standard table", len(rows)))
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Method 2: role="table"
        print("\n--- Method 2: Role-based table ---")
        try:
            table = self.driver.find_element(By.CSS_SELECTOR, "[role='table']")
            rows = table.find_elements(By.CSS_SELECTOR, "[role='row']")
            print(f"✅ Found {len(rows)} rows with role='row'")
            
            if rows:
                # Skip header row
                data_rows = [r for r in rows if r.find_elements(By.CSS_SELECTOR, "[role='cell']")]
                print(f"   Data rows: {len(data_rows)}")
                
                if data_rows:
                    first_row = data_rows[0]
                    cells = first_row.find_elements(By.CSS_SELECTOR, "[role='cell']")
                    print(f"   First row has {len(cells)} cells")
                    print(f"   Cell contents: {[cell.text for cell in cells[:5]]}")
                    methods_tried.append(("Role-based table", len(data_rows)))
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Method 3: Find by text pattern
        print("\n--- Method 3: Find by text pattern ---")
        try:
            # Find all elements containing phone numbers
            phone_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '+1 2')]")
            print(f"✅ Found {len(phone_elements)} elements with phone numbers")
            
            if phone_elements:
                print(f"   First phone: {phone_elements[0].text}")
                methods_tried.append(("Text pattern", len(phone_elements)))
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        if methods_tried:
            print("✅ Working methods:")
            for method, count in methods_tried:
                print(f"   - {method}: {count} items")
        else:
            print("❌ No methods worked. The page structure may be different than expected.")
            print("   Please check page_source.html and page_screenshot.png")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
        print("\nBrowser closed")


def main():
    """Main function to run the debug scraper"""
    
    print("="*60)
    print("Hiya Phone Number Scraper - DEBUG MODE")
    print("="*60)
    print("\nThis will help us figure out why data isn't being scraped.")
    print("Files will be created for inspection:\n")
    print("  - page_source.html (HTML of the page)")
    print("  - page_screenshot.png (Screenshot)")
    print("\n")
    
    username = input("Enter your Hiya username/email: ")
    password = input("Enter your Hiya password: ")
    
    scraper = HiyaScraperDebug(headless=False)
    
    try:
        # Login
        scraper.login(username, password)
        
        # Handle 2FA
        print("\nIf you have 2FA enabled, please complete it in the browser...")
        print("Press Enter once you're logged in and ready to continue...")
        input()
        
        # Navigate
        scraper.navigate_to_phone_numbers()
        
        # Give page time to fully load
        print("\nWaiting for page to fully load...")
        time.sleep(3)
        
        # Inspect the page
        scraper.inspect_page()
        
        # Try different scraping methods
        scraper.try_scraping_methods()
        
        print("\n" + "="*60)
        print("DEBUG COMPLETE")
        print("="*60)
        print("\nPlease review the output above and the generated files.")
        print("The browser will stay open for 30 seconds so you can inspect manually.")
        time.sleep(30)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nBrowser will stay open for 60 seconds for manual inspection...")
        time.sleep(60)
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
