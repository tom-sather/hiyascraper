"""
Hiya Phone Number Scraper - DEBUG VERSION
This will help us see what's actually on the page
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class HiyaScraperDebug:
    def __init__(self):
        """Initialize the scraper with Chrome webdriver"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
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
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.wait = WebDriverWait(self.driver, 15)
        
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
            time.sleep(5)
            print("✅ Login complete!")
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            raise
    
    def inspect_page(self, page_num=0):
        """Navigate to a page and inspect its structure"""
        url = f"https://business.hiya.com/registration/cross-carrier-registration/phones?search=&status=&hasBrandedCall=&page={page_num}&size=100&sortDirection=desc&sortBy=submittedAt"
        
        print(f"\n{'='*60}")
        print(f"INSPECTING PAGE {page_num}")
        print(f"{'='*60}")
        print(f"URL: {url}")
        
        self.driver.get(url)
        
        # Wait for initial load
        print("\nWaiting 5 seconds for page to load...")
        time.sleep(5)
        
        # Try different wait times
        print("\nTrying 10 second wait...")
        time.sleep(5)
        
        print(f"\nCurrent URL: {self.driver.current_url}")
        
        # Save page source
        page_source = self.driver.page_source
        filename = f'page_{page_num}_source.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"✅ Saved page source to '{filename}'")
        
        # Save screenshot
        screenshot_file = f'page_{page_num}_screenshot.png'
        self.driver.save_screenshot(screenshot_file)
        print(f"✅ Saved screenshot to '{screenshot_file}'")
        
        # Check for various elements
        print("\n" + "-"*60)
        print("ELEMENT DETECTION")
        print("-"*60)
        
        # Look for tables
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        print(f"\n<table> elements: {len(tables)}")
        
        if tables:
            for i, table in enumerate(tables):
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"  Table {i+1}: {len(rows)} <tr> elements")
        
        # Look for tbody
        tbody_elements = self.driver.find_elements(By.TAG_NAME, "tbody")
        print(f"\n<tbody> elements: {len(tbody_elements)}")
        
        if tbody_elements:
            for i, tbody in enumerate(tbody_elements):
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                print(f"  tbody {i+1}: {len(rows)} <tr> elements")
        
        # Look for role-based elements
        role_tables = self.driver.find_elements(By.CSS_SELECTOR, "[role='table']")
        print(f"\n[role='table'] elements: {len(role_tables)}")
        
        role_rows = self.driver.find_elements(By.CSS_SELECTOR, "[role='row']")
        print(f"[role='row'] elements: {len(role_rows)}")
        
        role_cells = self.driver.find_elements(By.CSS_SELECTOR, "[role='cell']")
        print(f"[role='cell'] elements: {len(role_cells)}")
        
        # Look for phone numbers in text
        print("\n" + "-"*60)
        print("TEXT CONTENT SEARCH")
        print("-"*60)
        
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        
        if "+1 2" in body_text:
            print("✅ Found phone number pattern '+1 2' in page text")
            lines = [line for line in body_text.split('\n') if '+1 2' in line]
            print(f"   Found {len(lines)} lines with phone numbers")
            if lines:
                print(f"   First 3 lines:")
                for line in lines[:3]:
                    print(f"     {line[:80]}")
        else:
            print("❌ No phone number pattern '+1 2' found in page text")
        
        if "1,331" in body_text or "phone numbers" in body_text.lower():
            print("✅ Found 'phone numbers' or count in text")
        else:
            print("❌ No 'phone numbers' text found")
        
        # Look for specific elements
        print("\n" + "-"*60)
        print("SPECIFIC ELEMENT SEARCH")
        print("-"*60)
        
        # Try to find any divs that might contain the data
        all_divs = self.driver.find_elements(By.TAG_NAME, "div")
        print(f"\nTotal <div> elements: {len(all_divs)}")
        
        # Look for Material-UI or other common table classes
        mui_classes = [
            "MuiTable",
            "MuiTableBody",
            "MuiTableRow",
            "MuiTableCell",
            "ant-table",
            "data-grid",
            "table-row",
            "table-cell"
        ]
        
        for class_name in mui_classes:
            elements = self.driver.find_elements(By.CSS_SELECTOR, f"[class*='{class_name}']")
            if elements:
                print(f"✅ Found {len(elements)} elements with class containing '{class_name}'")
        
        # Check if there's a loading spinner or skeleton
        loading_indicators = self.driver.find_elements(By.CSS_SELECTOR, "[class*='loading'], [class*='Loading'], [class*='spinner'], [class*='Spinner'], [class*='skeleton'], [class*='Skeleton']")
        if loading_indicators:
            print(f"\n⚠️  Found {len(loading_indicators)} loading indicator elements")
            print("   Page might still be loading!")
        
        print("\n" + "="*60)
        print("INSPECTION COMPLETE")
        print("="*60)
        print("\nPlease check the saved files:")
        print(f"  - {filename}")
        print(f"  - {screenshot_file}")
        print("\nThe browser will stay open for 30 seconds for manual inspection...")
        time.sleep(30)
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
        print("Browser closed")


def main():
    """Main function"""
    print("="*60)
    print("Hiya Scraper - DEBUG MODE")
    print("="*60)
    print("\nThis will inspect the page structure to help fix the scraper.\n")
    
    username = input("Enter your Hiya username/email: ")
    password = input("Enter your Hiya password: ")
    
    scraper = HiyaScraperDebug()
    
    try:
        scraper.login(username, password)
        
        print("\n🔐 If you have 2FA, please complete it now...")
        print("Press Enter when ready...")
        input()
        
        # Inspect page 0 (first page with data)
        scraper.inspect_page(0)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(30)
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
