from selenium import webdriver
# Do NOT import Service, and do NOT specify an executable path

# Initialize the driver directly. Selenium Manager will automatically 
# find your Chrome v149 and download the correct matching driver.
driver = webdriver.Chrome() 

# Test the connection
driver.get("https://www.google.com")

# Optional: keep the browser open for a few seconds to verify
import time
time.sleep(5)
driver.quit()