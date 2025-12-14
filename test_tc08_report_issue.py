import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import USERNAME, PASSWORD  # Import the credentials

# Setup logging to log test results
log_file = "test_results.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

# Create a folder for screenshots if it doesn't exist
screenshots_folder = "screenshots"
os.makedirs(screenshots_folder, exist_ok=True)

def take_screenshot(driver, test_name, step_name):
    screenshot_path = os.path.join(screenshots_folder, f"{test_name}_{step_name}.png")
    driver.save_screenshot(screenshot_path)
    logging.info(f"Screenshot saved for {step_name} step: {screenshot_path}")
    return screenshot_path

def log_test_result(test_name, result, screenshot_path=None):
    if result:
        logging.info(f"Test '{test_name}' PASSED")
    else:
        logging.error(f"Test '{test_name}' FAILED. Screenshot: {screenshot_path}")

def login(driver):
    test_name = "report_issue_test"
    try:
        # Wait for the username field to be visible and enter username
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        take_screenshot(driver, test_name, "entered_username")

        # Click Login
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        take_screenshot(driver, test_name, "clicked_login_button")

        # Wait for the password field to appear
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, "password")))

        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        take_screenshot(driver, test_name, "entered_password")

        # Submit the login form
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        take_screenshot(driver, test_name, "submitted_form")

        # Wait until the next page (dashboard or landing page) is loaded
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='account_page.php']")))

        # Take screenshot of successful login
        screenshot_path = take_screenshot(driver, test_name, "login_successful")
        log_test_result(test_name, result=True, screenshot_path=screenshot_path)
        
    except Exception as e:
        screenshot_path = take_screenshot(driver, test_name, "login_failed")
        log_test_result(test_name, result=False, screenshot_path=screenshot_path)
        logging.error(f"Error occurred during login: {str(e)}")


def report_issue(driver):
    test_name = "report_issue_test"

    try:
        # Navigate to "Report Issue" section
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, "Report Issue"))).click()
        take_screenshot(driver, test_name, "clicked_report_issue")

        # Wait for the "Choose Project" dropdown to be clickable and interactable
        project_dropdown = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.NAME, "project_id")))

        # Ensure it's in view
        driver.execute_script("arguments[0].scrollIntoView(true);", project_dropdown)

        # Select the project (ensure correct value or option is being selected)
        project_dropdown.send_keys("MantisBT project")
        take_screenshot(driver, test_name, "selected_project")

        # Wait for the issue form to be visible and interactable
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, "category_id")))

        # Select the issue Category
        driver.find_element(By.NAME, "category_id").send_keys("General")
        take_screenshot(driver, test_name, "selected_category")

        # Select the Reproducibility option
        driver.find_element(By.NAME, "reproducibility").send_keys("have not tried")
        take_screenshot(driver, test_name, "selected_reproducibility")

        # Select Severity and Priority
        driver.find_element(By.NAME, "severity").send_keys("minor")
        take_screenshot(driver, test_name, "selected_severity")

        driver.find_element(By.NAME, "priority").send_keys("normal")
        take_screenshot(driver, test_name, "selected_priority")

        # Fill in the summary
        driver.find_element(By.NAME, "summary").send_keys("Issue reported via Selenium automation")
        take_screenshot(driver, test_name, "entered_summary")

        # Fill in the description
        driver.find_element(By.NAME, "description").send_keys("This issue was automatically reported using Selenium for testing purposes.")
        take_screenshot(driver, test_name, "entered_description")

        # Scroll down to the submit button and wait for it to be clickable
        submit_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))

        # Click on "Submit Issue"
        submit_button.click()
        take_screenshot(driver, test_name, "clicked_submit_issue")

        # Wait for the confirmation of issue submission
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2")))

        # Take screenshot of the confirmation
        screenshot_path = take_screenshot(driver, test_name, "issue_reported_successfully")
        log_test_result(test_name, result=True, screenshot_path=screenshot_path)

    except Exception as e:
        screenshot_path = take_screenshot(driver, test_name, "issue_report_failed")
        log_test_result(test_name, result=False, screenshot_path=screenshot_path)
        logging.error(f"Error occurred during issue reporting: {str(e)}")

    test_name = "report_issue_test"

    try:
        # Navigate to "Report Issue" section
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, "Report Issue"))).click()
        take_screenshot(driver, test_name, "clicked_report_issue")

        # Wait for "Choose Project" dropdown and select a project
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.NAME, "project_id"))).send_keys("MantisBT project")
        take_screenshot(driver, test_name, "selected_project")

        # Wait for the issue form to be visible
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, "category_id")))

        # Select the issue Category
        driver.find_element(By.NAME, "category_id").send_keys("General")
        take_screenshot(driver, test_name, "selected_category")

        # Select the Reproducibility option
        driver.find_element(By.NAME, "reproducibility").send_keys("have not tried")
        take_screenshot(driver, test_name, "selected_reproducibility")

        # Select Severity and Priority
        driver.find_element(By.NAME, "severity").send_keys("minor")
        take_screenshot(driver, test_name, "selected_severity")

        driver.find_element(By.NAME, "priority").send_keys("normal")
        take_screenshot(driver, test_name, "selected_priority")

        # Fill in the summary
        driver.find_element(By.NAME, "summary").send_keys("Issue reported via Selenium automation")
        take_screenshot(driver, test_name, "entered_summary")

        # Fill in the description
        driver.find_element(By.NAME, "description").send_keys("This issue was automatically reported using Selenium for testing purposes.")
        take_screenshot(driver, test_name, "entered_description")

        # Scroll down to the submit button and wait for it to be clickable
        submit_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))

        # Click on "Submit Issue"
        submit_button.click()
        take_screenshot(driver, test_name, "clicked_submit_issue")

        # Wait for the confirmation of issue submission
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2")))

        # Take screenshot of the confirmation
        screenshot_path = take_screenshot(driver, test_name, "issue_reported_successfully")
        log_test_result(test_name, result=True, screenshot_path=screenshot_path)

    except Exception as e:
        screenshot_path = take_screenshot(driver, test_name, "issue_report_failed")
        log_test_result(test_name, result=False, screenshot_path=screenshot_path)
        logging.error(f"Error occurred during issue reporting: {str(e)}")


# Example usage:
def run_test():
    # Setup the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("http://localhost/mantis/login_page.php")  # Replace with your actual URL

    # Run the login test
    login(driver)

    # Run the report issue test
    report_issue(driver)

    # Close the driver after testing
    driver.quit()

if __name__ == "__main__":
    run_test()
