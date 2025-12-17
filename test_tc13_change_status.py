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

def login(driver):
    test_name = "login_test"
    try:
        print("🔐 Starting login...")
        
        # Navigate to login page
        driver.get("http://localhost/mantis/login_page.php")
        time.sleep(2)
        
        # Enter username
        username_field = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys(USERNAME)
        take_screenshot(driver, test_name, "entered_username")
        print("✓ Username entered")
        
        # Click to go to password page
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(2)
        take_screenshot(driver, test_name, "clicked_login_button")
        
        # Enter password
        password_field = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(PASSWORD)
        take_screenshot(driver, test_name, "entered_password")
        print("✓ Password entered")
        
        # Submit login
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(3)
        take_screenshot(driver, test_name, "submitted_form")
        
        # Verify login success
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "My View"))
        )
        
        take_screenshot(driver, test_name, "login_successful")
        log_test_result(test_name, True, "Login successful")
        print("✅ Login successful")
        return True
        
    except Exception as e:
        take_screenshot(driver, test_name, "login_failed")
        log_test_result(test_name, False, f"Login error: {str(e)}")
        print(f"❌ Login failed: {str(e)}")
        raise

def change_status(driver):
    test_name = "change_status_test"
    
    try:
        print("\n🔄 Starting status change test...")
        
        # Navigate to "View Issues" section
        print("Looking for View Issues link...")
        
        view_issues_link = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "View Issues"))
        )
        view_issues_link.click()
        time.sleep(3)
        take_screenshot(driver, test_name, "clicked_view_issues")
        print("✓ Clicked View Issues")
        
        # Find and click on an issue
        print("Looking for issue links...")
        issue_links = driver.find_elements(
            By.XPATH, "//a[contains(@href, 'view.php?id=')]"
        )
        
        if not issue_links:
            raise Exception("No issue links found")
        
        print(f"Found {len(issue_links)} potential issue links")
        
        # Click on the first issue link
        first_issue = issue_links[0]
        issue_id = first_issue.text.strip()
        print(f"Clicking on issue: {issue_id}")
        first_issue.click()
        time.sleep(3)
        take_screenshot(driver, test_name, "clicked_issue_link")
        print(f"✓ Clicked issue {issue_id}")
        
        # **STEP 1: Click on "Edit" text/link**
        print("Looking for Edit link/button...")
        
        # Try multiple ways to find Edit
        edit_found = False
        edit_selectors = [
            (By.LINK_TEXT, "Edit"),
            (By.PARTIAL_LINK_TEXT, "Edit"),
            (By.XPATH, "//a[contains(text(), 'Edit')]"),
            (By.XPATH, "//input[@value='Edit']"),
            (By.XPATH, "//button[contains(text(), 'Edit')]"),
        ]
        
        for selector in edit_selectors:
            try:
                edit_elements = driver.find_elements(*selector)
                if edit_elements:
                    edit_element = edit_elements[0]
                    print(f"Found Edit element: {edit_element.text} | {edit_element.get_attribute('value')}")
                    
                    # Scroll to Edit element
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_element)
                    time.sleep(1)
                    
                    # Click Edit
                    edit_element.click()
                    edit_found = True
                    print("✓ Clicked Edit")
                    break
            except:
                continue
        
        if not edit_found:
            print("❌ Edit link/button not found")
            take_screenshot(driver, test_name, "edit_not_found")
            
            # Debug: list all links on page
            all_links = driver.find_elements(By.TAG_NAME, "a")
            print(f"All links on page ({len(all_links)}):")
            for i, link in enumerate(all_links[:15]):  # Show first 15
                text = link.text.strip()
                href = link.get_attribute('href') or ''
                if text:
                    print(f"  {i+1}. '{text}' -> {href[:50]}...")
            
            raise Exception("Edit link/button not found")
        
        time.sleep(2)
        take_screenshot(driver, test_name, "clicked_edit")
        
        # **STEP 2: Find status dropdown and select "resolved"**
        print("Looking for status dropdown after clicking Edit...")
        
        # Wait for page to load/change
        time.sleep(2)
        
        # Try multiple ways to find status dropdown
        status_dropdown = None
        status_selectors = [
            (By.NAME, "status"),
            (By.ID, "status"),
            (By.XPATH, "//select[@name='status']"),
            (By.XPATH, "//select[contains(@name, 'status')]"),
            (By.XPATH, "//select[option[contains(text(), 'resolved')]]"),
        ]
        
        for selector in status_selectors:
            try:
                elements = driver.find_elements(*selector)
                if elements:
                    status_dropdown = elements[0]
                    print(f"✓ Found status dropdown using {selector[1]}")
                    break
            except:
                continue
        
        if not status_dropdown:
            # Debug: list all select elements
            all_selects = driver.find_elements(By.TAG_NAME, "select")
            print(f"No status dropdown found. Found {len(all_selects)} select elements:")
            for i, select in enumerate(all_selects):
                name = select.get_attribute('name') or 'no-name'
                id_attr = select.get_attribute('id') or 'no-id'
                print(f"  Select {i+1}: name='{name}', id='{id_attr}'")
            
            take_screenshot(driver, test_name, "no_status_dropdown")
            raise Exception("Status dropdown not found after clicking Edit")
        
        # Select "resolved" from dropdown
        select = Select(status_dropdown)
        
        # List available options
        options = select.options
        print(f"Available status options ({len(options)}):")
        for i, option in enumerate(options):
            print(f"  {i+1}. '{option.text}'")
        
        # Select "resolved"
        for option in options:
            if "resolved" in option.text.lower():
                select.select_by_visible_text(option.text)
                print(f"✓ Selected status: '{option.text}'")
                break
        
        take_screenshot(driver, test_name, "selected_resolved")
        
        # **STEP 3: Scroll down and find "Update" button**
        print("Looking for Update button...")
        
        # Find all Update buttons
        update_buttons = driver.find_elements(
            By.XPATH, "//input[@type='submit' and (@value='Update Information' or @value='Update' or contains(@value, 'Update'))]"
        )
        
        if not update_buttons:
            # Try any submit button
            update_buttons = driver.find_elements(By.XPATH, "//input[@type='submit']")
        
        if not update_buttons:
            # Try buttons with text "Update"
            update_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Update')]")
        
        if not update_buttons:
            # Last resort: any button
            update_buttons = driver.find_elements(By.XPATH, "//button")
        
        print(f"Found {len(update_buttons)} potential update buttons")
        
        if update_buttons:
            # Find the right Update button
            update_button = None
            for btn in update_buttons:
                if btn.is_displayed():
                    btn_text = btn.get_attribute('value') or btn.text or ''
                    print(f"  Button: '{btn_text}'")
                    
                    # Look for Update button
                    if 'update' in btn_text.lower():
                        update_button = btn
                        break
            
            if not update_button and update_buttons:
                # Use first displayed button
                for btn in update_buttons:
                    if btn.is_displayed():
                        update_button = btn
                        break
            
            if update_button:
                # Scroll to the button
                print("Scrolling to Update button...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", update_button)
                time.sleep(1)
                
                # Take screenshot before clicking
                take_screenshot(driver, test_name, "before_update_click")
                
                # Click the button
                btn_text = update_button.get_attribute('value') or update_button.text or 'Update'
                print(f"Clicking button: '{btn_text}'")
                update_button.click()
                print("✓ Clicked Update button")
                
                time.sleep(3)
                take_screenshot(driver, test_name, "clicked_update_button")
                
                # **STEP 4: Verify the status actually changed**
                print("Verifying status change...")
                
                # Check current page
                current_url = driver.current_url
                page_source = driver.page_source
                
                # Check for success indicators
                success = False
                success_indicators = [
                    "Operation successful",
                    "updated successfully",
                    "Status changed",
                    "resolved"
                ]
                
                for indicator in success_indicators:
                    if indicator.lower() in page_source.lower():
                        success = True
                        print(f"✓ Success indicator: '{indicator}'")
                        break
                
                # Also check if status is shown as resolved on page
                if "resolved" in page_source.lower():
                    # Look for status text on page
                    status_patterns = [
                        "Status:",
                        "Current Status:",
                        "Issue Status:"
                    ]
                    
                    for pattern in status_patterns:
                        if pattern in page_source:
                            # Try to extract status
                            import re
                            match = re.search(f"{pattern}[^<]*resolved", page_source, re.IGNORECASE)
                            if match:
                                print(f"✅ Status confirmed: {match.group(0)}")
                                success = True
                                break
                
                if success:
                    print("✅ Status changed successfully!")
                    take_screenshot(driver, test_name, "status_changed_success")
                    log_test_result(test_name, True, f"Status changed to Resolved for issue {issue_id}")
                    return True
                else:
                    print("⚠ Could not confirm status change in page")
                    take_screenshot(driver, test_name, "status_change_not_confirmed")
                    log_test_result(test_name, False, "Could not confirm status change")
                    return False
            else:
                print("❌ No Update button found that is clickable")
                take_screenshot(driver, test_name, "no_update_button")
                return False
        else:
            print("❌ No Update buttons found at all")
            take_screenshot(driver, test_name, "no_buttons_found")
            return False
        
    except Exception as e:
        take_screenshot(driver, test_name, "status_change_failed")
        error_msg = f"Status change failed: {str(e)}"
        print(f"❌ {error_msg}")
        log_test_result(test_name, False, error_msg)
        raise


    """Simplified version that mimics manual steps"""
    test_name = "change_status_simple_test"
    
    try:
        print("\n🔄 Starting simplified status change test...")
        
        # Go to View Issues
        driver.get("http://localhost/mantis/view_all_bug_page.php")
        time.sleep(3)
        
        # Click first issue
        issue_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'view.php?id=')]")
        if not issue_links:
            raise Exception("No issues found")
        
        issue_links[0].click()
        time.sleep(3)
        
        # **METHOD 1: Try to find and click "Change Status" link/button**
        print("Looking for Change Status link...")
        
        # Look for links containing "Change Status"
        change_status_links = driver.find_elements(
            By.XPATH, "//a[contains(text(), 'Change Status') or contains(@href, 'bug_change_status_page.php')]"
        )
        
        if change_status_links:
            print(f"Found {len(change_status_links)} Change Status links")
            change_status_links[0].click()
            time.sleep(2)
        else:
            # Look for buttons
            change_status_buttons = driver.find_elements(
                By.XPATH, "//input[@value='Change Status' or @value='Change Status To']"
            )
            if change_status_buttons:
                change_status_buttons[0].click()
                time.sleep(2)
        
        # Now we should be on status change page
        take_screenshot(driver, test_name, "on_status_change_page")
        
        # Select resolved
        status_select = Select(driver.find_element(By.NAME, "new_status"))
        status_select.select_by_visible_text("resolved")
        print("✓ Selected 'resolved' status")
        
        # **IMPORTANT: Also fill resolution if required**
        try:
            resolution_select = Select(driver.find_element(By.NAME, "resolution"))
            resolution_select.select_by_visible_text("fixed")
            print("✓ Selected resolution: 'fixed'")
        except:
            print("⚠ No resolution dropdown found (may not be required)")
        
        # Find and click the main update button
        update_buttons = driver.find_elements(
            By.XPATH, "//input[@type='submit' and (@value='Update Status' or @value='Change Status' or @value='Submit')]"
        )
        
        if update_buttons:
            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView(true);", update_buttons[0])
            time.sleep(1)
            
            # Take screenshot before click
            take_screenshot(driver, test_name, "before_status_update")
            
            update_buttons[0].click()
            print("✓ Clicked update status button")
            time.sleep(3)
            
            # Verify success
            if "Operation successful" in driver.page_source:
                print("✅ Status changed successfully!")
                return True
            else:
                print("⚠ Could not verify success")
                return False
        else:
            print("❌ No update button found")
            return False
            
    except Exception as e:
        print(f"❌ Simplified method failed: {str(e)}")
        raise
def run_test():
    print("="*60)
    print("MANTISBT SELENIUM TEST - CHANGE ISSUE STATUS")
    print("="*60)
    
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        # Run login test
        login_success = False
        try:
            login_success = login(driver)
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
        
        if login_success:
            # Run status change test
            try:
                change_status(driver)
            except Exception as e:
                print(f"❌ Status change failed: {str(e)}")
        
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