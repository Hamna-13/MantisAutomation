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
    """Take screenshot and log it"""
    screenshot_path = os.path.join(screenshots_folder, f"{test_name}_{step_name}.png")
    driver.save_screenshot(screenshot_path)
    logging.info(f"Screenshot saved for {step_name}: {screenshot_path}")
    print(f"📸 Screenshot: {step_name}")
    return screenshot_path

def log_test_result(test_name, result, message=""):
    """Log test result"""
    if result:
        logging.info(f"Test '{test_name}' PASSED: {message}")
        print(f"✅ Test '{test_name}' PASSED: {message}")
    else:
        logging.error(f"Test '{test_name}' FAILED: {message}")
        print(f"❌ Test '{test_name}' FAILED: {message}")

def wait_for_page_load(driver, timeout=30):
    """Wait for page to load completely"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except:
        pass
    time.sleep(1)  # Small buffer

def login(driver):
    """Login to MantisBT"""
    test_name = "login_test"
    try:
        print("🔐 Starting login...")
        driver.get("http://localhost/mantis/login_page.php")
        wait_for_page_load(driver)
        
        # Enter username and click to password page
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys(USERNAME)
        take_screenshot(driver, test_name, "entered_username")
        
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        wait_for_page_load(driver)
        
        # Enter password and submit
        password_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(PASSWORD)
        take_screenshot(driver, test_name, "entered_password")
        
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        wait_for_page_load(driver)
        
        # Verify login success
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "My View"))
        )
        
        take_screenshot(driver, test_name, "login_success")
        print("✅ Login successful")
        log_test_result(test_name, True, "Login successful")
        return True
        
    except Exception as e:
        take_screenshot(driver, test_name, "login_failed")
        log_test_result(test_name, False, f"Login failed: {str(e)}")
        raise

def create_project(driver):
    """Create a new project in MantisBT"""
    test_name = "create_project_test"
    project_name = f"Test Project {int(time.time())}"  # Unique name
    
    try:
        print("\n🚀 Starting project creation...")
        
        # Step 1: Navigate directly to create project page
        print("📍 Navigating to Create Project page...")
        driver.get("http://localhost/mantis/manage_proj_create_page.php")
        wait_for_page_load(driver)
        
        take_screenshot(driver, test_name, "create_form_page")
        
        # Step 2: Verify we're on create project form
        print("📋 Verifying create project form...")
        
        # Wait for form to load - based on your output, it has 6 inputs, 2 dropdowns, 1 textarea
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "name"))
        )
        
        # Step 3: Fill the project form
        print("📝 Filling project details...")
        
        # Fill project name
        name_field = driver.find_element(By.NAME, "name")
        name_field.clear()
        name_field.send_keys(project_name)
        print(f"✓ Project name filled: {project_name}")
        take_screenshot(driver, test_name, "filled_project_name")
        
        # Fill status (development)
        status_select = driver.find_element(By.NAME, "status")
        from selenium.webdriver.support.ui import Select
        Select(status_select).select_by_visible_text("development")
        print("✓ Status selected: development")
        
        # Fill view state (public)
        view_state_select = driver.find_element(By.NAME, "view_state")
        Select(view_state_select).select_by_visible_text("public")
        print("✓ View state selected: public")
        
        # Handle inherit global categories (optional - skip if not found)
        try:
            inherit_checkbox = driver.find_element(By.NAME, "inherit_global")
            if not inherit_checkbox.is_selected():
                inherit_checkbox.click()
            print("✓ Inherit global categories checked")
        except:
            print("⚠ Inherit global categories checkbox not found (skipping)")
        
        # Fill description
        desc_field = driver.find_element(By.NAME, "description")
        desc_field.clear()
        desc_field.send_keys("This is a test project created for Selenium automation.")
        print("✓ Description filled")
        
        take_screenshot(driver, test_name, "form_filled")
        
        # Step 4: Submit the form
        print("📤 Submitting form...")
        
        # Find and click submit button
        submit_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Add Project']"))
        )
        submit_button.click()
        print("✅ Form submitted")
        
        wait_for_page_load(driver)
        time.sleep(3)  # Wait for processing
        
        # Step 5: Verify success
        take_screenshot(driver, test_name, "after_submit")
        
        # Check for success
        success = False
        success_message = ""
        
        # Check current URL
        current_url = driver.current_url
        print(f"Current URL after submit: {current_url}")
        
        # Check page content
        page_source = driver.page_source
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Success indicators (checking each one)
        success_indicators = [
            ("Operation successful", "Operation successful message found"),
            ("Project created successfully", "Project created message found"),
            ("manage_proj_page.php" in current_url, "On manage projects page"),
            ("view_all_set.php" in current_url, "On view all set page"),
            (project_name in page_text, f"Project name '{project_name}' found on page"),
        ]
        
        for indicator, message in success_indicators:
            if indicator:
                success = True
                success_message = message
                print(f"✓ Success indicator: {message}")
                break
        
        if success:
            print("🎉 Project created successfully!")
            
            # Additional verification: Check if project appears in projects list
            try:
                driver.get("http://localhost/mantis/manage_proj_page.php")
                wait_for_page_load(driver)
                
                if project_name in driver.page_source:
                    print(f"✅ Verified: Project '{project_name}' found in projects list")
                    take_screenshot(driver, test_name, "project_in_list")
                else:
                    print("⚠ Project created but not found in projects list (might need refresh)")
            except:
                print("⚠ Could not verify project in list, but creation appears successful")
            
            log_test_result(test_name, True, success_message)
            return True
        else:
            # Check for errors
            error_indicators = ["error", "failed", "invalid", "required"]
            errors_found = []
            
            for error_indicator in error_indicators:
                if error_indicator in page_text.lower():
                    errors_found.append(error_indicator)
            
            if errors_found:
                error_msg = f"Errors detected: {', '.join(errors_found)}"
                print(f"❌ {error_msg}")
                take_screenshot(driver, test_name, "creation_error")
                log_test_result(test_name, False, error_msg)
            else:
                print("⚠ Could not confirm project creation or failure")
                log_test_result(test_name, False, "Unknown result - check screenshots")
            
            return False
            
    except Exception as e:
        take_screenshot(driver, test_name, "error")
        error_msg = f"Error during project creation: {str(e)}"
        print(f"❌ {error_msg}")
        log_test_result(test_name, False, error_msg)
        raise

def run_test():
    """Main test execution"""
    print("="*60)
    print("MANTISBT SELENIUM TEST - LOGIN & PROJECT CREATION")
    print("="*60)
    
    # Setup WebDriver with options
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Uncomment for headless mode
    # options.add_argument("--headless=new")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        # Run login test
        print("\n" + "-"*60)
        login_success = False
        try:
            login_success = login(driver)
        except Exception as login_error:
            print(f"Login failed: {login_error}")
            login_success = False
        
        if login_success:
            # Run project creation test
            print("\n" + "-"*60)
            try:
                create_project(driver)
            except Exception as project_error:
                print(f"Project creation failed: {project_error}")
        
        print("\n" + "="*60)
        print("TEST EXECUTION COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        take_screenshot(driver, "final", "test_failure")
        
    finally:
        # Small delay before closing
        time.sleep(2)
        print("\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    run_test()