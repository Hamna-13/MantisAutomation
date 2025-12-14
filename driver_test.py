from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://www.google.com")
print("Opened:", driver.title)
driver.quit()
