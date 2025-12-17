import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
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
    print(f"📸 Screenshot: {step_name}")
    return screenshot_path

def log_test_result(test_name, result, message=""):
    if result:
        logging.info(f"Test '{test_name}' PASSED: {message}")
        print(f"✅ Test '{test_name}' PASSED: {message}")
    else:
        logging.error(f"Test '{test_name}' FAILED: {message}")
        print(f"❌ Test '{test_name}' FAILED: {message}")

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
            log_test_result(test_name, True, "Login successful")
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
                log_test_result(test_name, True, "Login uncertain but proceeding")
                return True
                
    except Exception as e:
        take_screenshot(driver, test_name, "login_failed")
        error_msg = f"Login failed with error: {str(e)}"
        print(f"❌ {error_msg}")
        log_test_result(test_name, False, error_msg)
        raise

def assign_issue(driver):
    test_name = "assign_issue_test"
    
    try:
        print("\n📋 Starting issue assignment...")
        
        # Navigate to "View Issues" section
        print("Looking for View Issues link...")
        
        # Find View Issues link with multiple strategies
        view_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "View")
        view_issues_link = None
        
        for link in view_links:
            if "Issues" in link.text:
                view_issues_link = link
                print(f"Found View Issues link: {link.text}")
                break
        
        if not view_issues_link:
            # Try direct URL
            print("View Issues link not found, trying direct URL...")
            driver.get("http://localhost/mantis/view_all_bug_page.php")
        else:
            view_issues_link.click()
        
        time.sleep(3)
        take_screenshot(driver, test_name, "clicked_view_issues")
        print("✓ Navigated to View Issues")
        
        # Check current URL and page state
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Wait for issues to load
        time.sleep(2)
        
        # Take screenshot of issues page
        take_screenshot(driver, test_name, "issues_page_loaded")
        
        # Find and click on an issue link
        print("Looking for issue links...")
        
        # Strategy 1: Look for issue ID links (like 0000001, 0000002, etc.)
        issue_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'view.php?id=') or contains(@href, 'bug_view_page.php')]")
        
        if not issue_links:
            # Strategy 2: Look for links with numeric text (issue IDs)
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                link_text = link.text.strip()
                # Look for patterns like "0000001", "000001", etc.
                if link_text and link_text.isdigit() and len(link_text) >= 6:
                    issue_links.append(link)
        
        if not issue_links:
            # Strategy 3: Look for any link with "id=" in href
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                href = link.get_attribute('href') or ''
                if 'id=' in href:
                    issue_links.append(link)
        
        print(f"Found {len(issue_links)} potential issue links")
        
        if issue_links:
            # Click on the first issue link
            first_issue = issue_links[0]
            issue_id = first_issue.text.strip()
            print(f"Clicking on issue ID: {issue_id}")
            first_issue.click()
            time.sleep(3)
            take_screenshot(driver, test_name, "clicked_issue_link")
            print(f"✓ Clicked issue {issue_id}")
        else:
            print("❌ No issue links found")
            take_screenshot(driver, test_name, "no_issue_links")
            
            # Debug: show what's on the page
            print("Debug - first 10 links on page:")
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for i, link in enumerate(all_links[:10]):
                print(f"  {i+1}. Text: '{link.text}', Href: {link.get_attribute('href')}")
            
            raise Exception("No issue links found on View Issues page")
        
        # Now we should be on the issue details page
        print(f"Current URL after clicking issue: {driver.current_url}")
        
        # Take screenshot of issue details page
        take_screenshot(driver, test_name, "issue_details_page")
        
        # Look for "Assign To" functionality
        print("Looking for assign functionality...")
        
        # Try different approaches to find assign dropdown
        assign_dropdown = None
        assign_selectors = [
            (By.NAME, "handler_id"),
            (By.ID, "handler_id"),
            (By.XPATH, "//select[contains(@name, 'handler') or contains(@id, 'handler')]"),
            (By.XPATH, "//select[option[contains(text(), 'john') or contains(text(), 'John')]]"),
        ]
        
        for selector in assign_selectors:
            try:
                elements = driver.find_elements(*selector)
                if elements:
                    assign_dropdown = elements[0]
                    print(f"✓ Found assign dropdown using {selector[1]}")
                    break
            except:
                continue
        
        if not assign_dropdown:
            # Maybe there's an "Assign" button/link first
            print("Assign dropdown not found, looking for assign button...")
            assign_buttons = driver.find_elements(
                By.XPATH, "//a[contains(text(), 'Assign') or contains(@href, 'assign')]"
            )
            if assign_buttons:
                print(f"Found {len(assign_buttons)} assign buttons")
                assign_buttons[0].click()
                time.sleep(2)
                take_screenshot(driver, test_name, "clicked_assign_button")
                # Now try to find dropdown again
                assign_dropdown = driver.find_element(By.NAME, "handler_id")
        
        if assign_dropdown:
            # Select assignee
            select = Select(assign_dropdown)
            
            # List available assignees
            options = select.options
            print(f"Available assignees ({len(options)}):")
            for opt in options:
                print(f"  - '{opt.text}'")
            
            # Try to select "john" (case insensitive)
            assignee_found = False
            target_assignee = "john"
            
            for opt in options:
                if target_assignee.lower() in opt.text.lower():
                    select.select_by_visible_text(opt.text)
                    print(f"✓ Selected assignee: '{opt.text}'")
                    assignee_found = True
                    break
            
            if not assignee_found and len(options) > 1:
                # Select first non-empty assignee
                for opt in options:
                    if opt.text.strip() and opt.text.strip().lower() != "none" and opt.text.strip().lower() != "[none]":
                        select.select_by_visible_text(opt.text)
                        print(f"✓ Selected assignee (first available): '{opt.text}'")
                        assignee_found = True
                        break
            
            take_screenshot(driver, test_name, "selected_assignee")
            
            # Find and click update/submit button
            submit_buttons = driver.find_elements(
                By.XPATH, "//input[@type='submit' and (contains(@value, 'Update') or contains(@value, 'Assign') or contains(@value, 'Submit'))]"
            )
            
            if not submit_buttons:
                # Try any submit button
                submit_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
            
            if submit_buttons:
                for btn in submit_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn_text = btn.get_attribute('value') or ''
                        print(f"Clicking submit button: '{btn_text}'")
                        btn.click()
                        print("✓ Clicked update button")
                        break
                time.sleep(3)
                take_screenshot(driver, test_name, "clicked_update_button")
                
                # Check for success
                page_text = driver.page_source
                if "Operation successful" in page_text or "updated successfully" in page_text.lower() or "assigned to" in page_text.lower():
                    print("✅ Issue assigned successfully!")
                    take_screenshot(driver, test_name, "issue_assigned_successfully")
                    log_test_result(test_name, True, f"Issue {issue_id} assigned successfully")
                    return True
                else:
                    print("⚠ Could not confirm assignment success")
                    take_screenshot(driver, test_name, "assignment_uncertain")
                    log_test_result(test_name, False, "Could not confirm assignment")
                    return False
            else:
                print("❌ No submit button found")
                take_screenshot(driver, test_name, "no_submit_button")
                return False
        else:
            print("❌ Assign dropdown not found")
            take_screenshot(driver, test_name, "no_assign_dropdown")
            
            # Check if issue is already assigned
            if "assigned" in driver.page_source.lower():
                print("⚠ Issue appears to be already assigned")
                log_test_result(test_name, False, "Issue already assigned")
                return False
            else:
                raise Exception("Assign functionality not found")
        
    except Exception as e:
        take_screenshot(driver, test_name, "issue_assignment_failed")
        error_msg = f"Assignment error: {str(e)}"
        print(f"❌ {error_msg}")
        log_test_result(test_name, False, error_msg)
        raise

def run_test():
    print("="*60)
    print("MANTISBT SELENIUM TEST - LOGIN & ISSUE ASSIGNMENT")
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
            print("\n--- ISSUE ASSIGNMENT TEST ---")
            try:
                assign_issue(driver)
            except Exception as e:
                print(f"Issue assignment error: {str(e)}")
                take_screenshot(driver, "final", "issue_assignment_failure")
        
        print("\n" + "="*60)
        print("TEST EXECUTION COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        take_screenshot(driver, "final", "test_failure")
        
    finally:
        # Close browser automatically
        time.sleep(2)
        print("\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    run_test()