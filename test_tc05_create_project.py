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
    test_name = "create_project_test"
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


def create_project(driver):
    test_name = "create_project_test"

    try:
        # Click on "Manage" and ensure it's clickable
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, "Manage"))).click()
        take_screenshot(driver, test_name, "clicked_manage_projects")

        # Wait for "Projects" to be clickable, then click
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, "Projects"))).click()
        take_screenshot(driver, test_name, "clicked_projects_tab")

        # Wait until the "Create New Project" button is visible and clickable
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, "Create New Project"))).click()
        take_screenshot(driver, test_name, "clicked_create_new_project")

        # Wait for the form fields to appear and be interactable
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, "name")))

        # Fill in the project details
        driver.find_element(By.NAME, "name").send_keys("Test Project")
        take_screenshot(driver, test_name, "entered_project_name")

        # Select the status dropdown (development)
        driver.find_element(By.NAME, "status").send_keys("development")
        take_screenshot(driver, test_name, "selected_status_development")

        # Check the "Inherit Global Categories" checkbox
        driver.find_element(By.NAME, "inherit_global_categories").click()
        take_screenshot(driver, test_name, "checked_inherit_global_categories")

        # Select View Status (public)
        driver.find_element(By.NAME, "view_state").send_keys("public")
        take_screenshot(driver, test_name, "selected_view_status_public")

        # Fill the description
        driver.find_element(By.NAME, "description").send_keys("This is a test project created for Selenium automation.")
        take_screenshot(driver, test_name, "entered_project_description")

        # Wait for the submit button to be clickable
        submit_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))

        # Click the "Add Project" button
        submit_button.click()
        take_screenshot(driver, test_name, "submitted_create_project_form")

        # Wait for the project to be created
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2")))

        # Take screenshot of the confirmation
        screenshot_path = take_screenshot(driver, test_name, "project_created_successfully")
        log_test_result(test_name, result=True, screenshot_path=screenshot_path)

    except Exception as e:
        screenshot_path = take_screenshot(driver, test_name, "project_creation_failed")
        log_test_result(test_name, result=False, screenshot_path=screenshot_path)
        logging.error(f"Error occurred during project creation: {str(e)}")


# Example usage:
def run_test():
    # Setup the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("http://localhost/mantis/login_page.php")  # Replace with your actual URL

    # Run the login test
    login(driver)

    # Run the create project test
    create_project(driver)

    # Close the driver after testing
    driver.quit()

if __name__ == "__main__":
    run_test()
