import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import USERNAME, PASSWORD

# Setup logging
log_file = "test_results.log"
logging.basicConfig(filename=log_file, level=logging.INFO, 
                   format="%(asctime)s - %(levelname)s - %(message)s")

# Create screenshots folder
screenshots_folder = "screenshots"
os.makedirs(screenshots_folder, exist_ok=True)

def take_screenshot(driver, test_name, step_name):
    screenshot_path = os.path.join(screenshots_folder, f"{test_name}_{step_name}.png")
    driver.save_screenshot(screenshot_path)
    logging.info(f"Screenshot saved: {test_name}_{step_name}")
    print(f"📸 Screenshot: {test_name}_{step_name}")
    return screenshot_path

def debug_page_state(driver, location="unknown"):
    """Debug function to print current page state"""
    print(f"\n🔍 DEBUG at {location}:")
    print(f"  URL: {driver.current_url}")
    print(f"  Title: {driver.title}")
    print(f"  Page source length: {len(driver.page_source)} characters")
    
    # Check for common elements
    check_elements = [
        ("username field", "//input[@name='username']"),
        ("login button", "//input[@type='submit']"),
        ("any form", "//form"),
        ("any input", "//input")
    ]
    
    for element_name, xpath in check_elements:
        elements = driver.find_elements(By.XPATH, xpath)
        print(f"  {element_name}: {len(elements)} found")

def login(driver):
    test_name = "login_test"
    try:
        print("🔐 Starting login...")
        
        # Go to login page
        login_url = "http://localhost/mantis/login_page.php"
        print(f"Navigating to: {login_url}")
        driver.get(login_url)
        
        # Wait for page to load
        time.sleep(3)  # Initial wait
        debug_page_state(driver, "after page load")
        
        # Check if we're on login page
        if "login" not in driver.current_url.lower():
            print(f"⚠ Not on login page. Current URL: {driver.current_url}")
            take_screenshot(driver, test_name, "not_on_login_page")
        
        # Take initial screenshot
        take_screenshot(driver, test_name, "initial_page")
        
        # METHOD 1: Try finding username field with multiple selectors
        username_field = None
        username_selectors = [
            (By.NAME, "username"),
            (By.ID, "username"),
            (By.XPATH, "//input[@type='text' and contains(@name, 'user')]"),
            (By.XPATH, "//input[@type='text']")
        ]
        
        for selector in username_selectors:
            try:
                elements = driver.find_elements(*selector)
                if elements:
                    username_field = elements[0]
                    print(f"✓ Found username field using {selector[1]}")
                    break
            except:
                continue
        
        if not username_field:
            print("❌ Could not find username field")
            take_screenshot(driver, test_name, "username_not_found")
            raise Exception("Username field not found")
        
        # Enter username
        username_field.clear()
        username_field.send_keys(USERNAME)
        take_screenshot(driver, test_name, "entered_username")
        print("✓ Username entered")
        
        # Find and click login button
        login_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        if login_buttons:
            login_buttons[0].click()
            print("✓ Login button clicked")
        else:
            # Try to submit form
            forms = driver.find_elements(By.TAG_NAME, "form")
            if forms:
                forms[0].submit()
                print("✓ Form submitted")
        
        take_screenshot(driver, test_name, "clicked_login_button")
        
        # Wait for password page
        time.sleep(2)
        debug_page_state(driver, "after username submission")
        
        # METHOD 2: Try finding password field
        password_field = None
        password_selectors = [
            (By.NAME, "password"),
            (By.ID, "password"),
            (By.XPATH, "//input[@type='password']")
        ]
        
        for selector in password_selectors:
            try:
                elements = driver.find_elements(*selector)
                if elements:
                    password_field = elements[0]
                    print(f"✓ Found password field using {selector[1]}")
                    break
            except:
                continue
        
        if not password_field:
            print("⚠ Password field not found, checking if already logged in")
            # Check if we're already logged in
            if "My View" in driver.page_source or "account_page.php" in driver.current_url:
                print("✓ Already logged in")
                take_screenshot(driver, test_name, "already_logged_in")
                return True
            else:
                take_screenshot(driver, test_name, "password_not_found")
                raise Exception("Password field not found")
        
        # Enter password
        password_field.clear()
        password_field.send_keys(PASSWORD)
        take_screenshot(driver, test_name, "entered_password")
        print("✓ Password entered")
        
        # Submit login
        submit_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        if submit_buttons:
            submit_buttons[0].click()
            print("✓ Submit button clicked")
        
        take_screenshot(driver, test_name, "submitted_form")
        
        # Wait for login to complete
        time.sleep(3)
        
        # Check for login success
        success_indicators = [
            "My View",
            "account_page.php",
            "View Issues",
            "Report Issue"
        ]
        
        login_success = False
        page_text = driver.page_source
        for indicator in success_indicators:
            if indicator in page_text:
                login_success = True
                print(f"✓ Login success indicator found: {indicator}")
                break
        
        if login_success:
            take_screenshot(driver, test_name, "login_successful")
            print("✅ Login successful")
            return True
        else:
            # Check for errors
            if "error" in page_text.lower() or "invalid" in page_text.lower():
                print("❌ Login error detected")
                take_screenshot(driver, test_name, "login_error_detected")
                raise Exception("Login failed - error message found")
            else:
                print("⚠ Could not confirm login success, but no errors found")
                take_screenshot(driver, test_name, "login_uncertain")
                # Continue anyway
                return True
                
    except Exception as e:
        take_screenshot(driver, test_name, "login_failed")
        print(f"❌ Login failed with error: {str(e)}")
        # Re-raise the exception
        raise

def report_issue(driver):
    test_name = "report_issue_test"
    
    try:
        print("\n📝 Starting issue reporting...")
        
        # Click Report Issue link
        report_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Report")
        for link in report_links:
            if "Issue" in link.text:
                print(f"Found Report Issue link: {link.text}")
                link.click()
                break
        
        time.sleep(2)
        take_screenshot(driver, test_name, "clicked_report_issue")
        
        # Handle project selection if needed
        if "select_proj" in driver.current_url or driver.find_elements(By.NAME, "project_id"):
            print("Project selection required...")
            try:
                from selenium.webdriver.support.ui import Select
                project_select = Select(driver.find_element(By.NAME, "project_id"))
                
                # Select "MantisBT project"
                project_select.select_by_visible_text("MantisBT project")
                print("✓ Selected MantisBT project")
                
                # Submit project selection
                submit_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
                if submit_buttons:
                    submit_buttons[0].click()
                    time.sleep(2)
            except Exception as e:
                print(f"⚠ Project selection failed: {str(e)}")
        
        # Now fill the bug report form
        print("Filling issue form...")
        time.sleep(2)
        
        # Take screenshot of form
        take_screenshot(driver, test_name, "issue_form")
        
        # FIXED: Select "Bug tracking Projects" category
        print("\n🎯 Selecting category...")
        try:
            from selenium.webdriver.support.ui import Select
            
            # Find category dropdown
            category_select = Select(driver.find_element(By.NAME, "category_id"))
            
            # List all available categories for debugging
            all_categories = category_select.options
            print(f"Available categories ({len(all_categories)}):")
            for i, option in enumerate(all_categories):
                print(f"  {i+1}. '{option.text}'")
            
            # Try to select "Bug tracking Projects" 
            # Note: The exact text might be "Bug tracking Projects" or similar
            target_category = "Bug tracking Projects"
            
            # Try exact match first
            try:
                category_select.select_by_visible_text(target_category)
                print(f"✓ Category selected: '{target_category}'")
            except:
                # Try case-insensitive match
                category_found = False
                for option in all_categories:
                    if target_category.lower() in option.text.lower():
                        category_select.select_by_visible_text(option.text)
                        print(f"✓ Category selected (case-insensitive): '{option.text}'")
                        category_found = True
                        break
                
                if not category_found:
                    # Try partial match
                    for option in all_categories:
                        if "bug" in option.text.lower() or "tracking" in option.text.lower():
                            category_select.select_by_visible_text(option.text)
                            print(f"✓ Category selected (partial match): '{option.text}'")
                            break
                    else:
                        # Select first non-empty category
                        for option in all_categories:
                            if option.text.strip() and option.text.strip() != "---":
                                category_select.select_by_visible_text(option.text)
                                print(f"✓ Category selected (first available): '{option.text}'")
                                break
        
        except Exception as e:
            print(f"⚠ Could not select category: {str(e)}")
            take_screenshot(driver, test_name, "category_error")
        
        # Fill reproducibility
        try:
            repro_select = Select(driver.find_element(By.NAME, "reproducibility"))
            repro_select.select_by_visible_text("have not tried")
            print("✓ Reproducibility selected")
        except:
            print("⚠ Could not select reproducibility")
        
        # Fill severity
        try:
            severity_select = Select(driver.find_element(By.NAME, "severity"))
            severity_select.select_by_visible_text("minor")
            print("✓ Severity selected")
        except:
            print("⚠ Could not select severity")
        
        # Fill priority
        try:
            priority_select = Select(driver.find_element(By.NAME, "priority"))
            priority_select.select_by_visible_text("normal")
            print("✓ Priority selected")
        except:
            print("⚠ Could not select priority")
        
        # Fill summary
        try:
            summary_field = driver.find_element(By.NAME, "summary")
            summary_field.clear()
            summary_field.send_keys(f"Issue reported via Selenium automation - {int(time.time())}")
            print("✓ Summary entered")
        except:
            print("⚠ Could not enter summary")
        
        # Fill description
        try:
            description_field = driver.find_element(By.NAME, "description")
            description_field.clear()
            description_field.send_keys("This issue was automatically reported using Selenium for testing purposes.")
            print("✓ Description entered")
        except:
            print("⚠ Could not enter description")
        
        take_screenshot(driver, test_name, "form_filled")
        
        # Submit the issue
        print("Submitting issue...")
        
        # Find submit button with specific text
        submit_button = None
        submit_selectors = [
            (By.XPATH, "//input[@type='submit' and contains(@value, 'Submit Issue')]"),
            (By.XPATH, "//input[@type='submit' and contains(@value, 'Submit')]"),
            (By.CSS_SELECTOR, "input[type='submit'][value*='Issue']"),
            (By.CSS_SELECTOR, "input[type='submit']")
        ]
        
        for selector in submit_selectors:
            try:
                buttons = driver.find_elements(*selector)
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        submit_button = btn
                        print(f"Found submit button: {btn.get_attribute('value')}")
                        break
                if submit_button:
                    break
            except:
                continue
        
        if submit_button:
            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(0.5)
            submit_button.click()
            print("✓ Issue submitted")
        else:
            print("❌ Could not find submit button")
            take_screenshot(driver, test_name, "no_submit_button")
            return False
        
        # Wait for submission to complete
        time.sleep(3)
        take_screenshot(driver, test_name, "after_submission")
        
        # Check for success
        current_url = driver.current_url
        page_text = driver.page_source
        
        # Success indicators
        success_indicators = [
            "Operation successful",
            "Issue reported successfully",
            "View Submitted Issue",
            "bug_id=" in current_url,
            "view.php?id=" in current_url,
            "Issue ID:"
        ]
        
        success_found = False
        for indicator in success_indicators:
            if isinstance(indicator, str) and indicator in page_text:
                success_found = True
                print(f"✓ Success indicator found: {indicator}")
                break
            elif not isinstance(indicator, str) and indicator:
                success_found = True
                print(f"✓ Success indicator found in URL")
                break
        
        if success_found:
            # Try to extract issue ID
            try:
                import re
                if "id=" in current_url:
                    match = re.search(r'id=(\d+)', current_url)
                    if match:
                        issue_id = match.group(1)
                        print(f"🎉 Issue reported successfully! Issue ID: {issue_id}")
                elif "Issue ID:" in page_text or "Issue #" in page_text:
                    match = re.search(r'Issue (?:ID: ?|# ?)(\d+)', page_text)
                    if match:
                        issue_id = match.group(1)
                        print(f"🎉 Issue reported successfully! Issue ID: {issue_id}")
                else:
                    print("🎉 Issue reported successfully!")
            except:
                print("🎉 Issue reported successfully!")
            
            take_screenshot(driver, test_name, "success")
            return True
        else:
            # Check for errors
            if "error" in page_text.lower() or "failed" in page_text.lower():
                print("❌ Error detected in page")
                take_screenshot(driver, test_name, "error_detected")
            else:
                print("⚠ Could not confirm issue submission")
                take_screenshot(driver, test_name, "uncertain")
            
            return False
            
    except Exception as e:
        take_screenshot(driver, test_name, "error")
        print(f"❌ Issue reporting failed: {str(e)}")
        raise
def run_test():
    print("="*60)
    print("MANTISBT SELENIUM TEST - LOGIN & ISSUE REPORTING")
    print("="*60)
    
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Add more options for stability
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    # Set timeouts
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(10)
    
    try:
        print("\n--- LOGIN TEST ---")
        login_success = False
        
        try:
            login_success = login(driver)
        except Exception as e:
            print(f"Login error: {str(e)}")
            # Take final screenshot
            take_screenshot(driver, "final", "login_failure")
        
        if login_success:
            print("\n--- ISSUE REPORTING TEST ---")
            try:
                report_issue(driver)
            except Exception as e:
                print(f"Issue reporting error: {str(e)}")
                take_screenshot(driver, "final", "issue_report_failure")
        
        print("\n" + "="*60)
        print("TEST EXECUTION COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        take_screenshot(driver, "final", "test_failure")
        
    finally:
        # Keep browser open for debugging
        driver.quit()

if __name__ == "__main__":
    run_test()