import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# URL of the summer camps catalog
url = "https://secure.rec1.com/CA/san-ramon-ca/catalog"
# Criteria for selection
day_range = "08/05-08/09"
time_range = "9am-12pm"

# Set up the WebDriver (assuming you have ChromeDriver installed)
driver = webdriver.Chrome()

# Open the web page
driver.get(url)
try:
    # Check if the page loaded successfully
    if driver.current_url != url:
        raise Exception(f"Failed to load the page. Current URL: {driver.current_url}")

    for checkbox_label in ['Camps', 'Elementary', 'Youth']:
        # Wait until the checkbox is present and clickable
        wait = WebDriverWait(driver, 10)
        checkbox_label = wait.until(EC.presence_of_element_located((By.XPATH, f"//label[contains(text(), '{checkbox_label}')]")))

        # Find the checkbox associated with the label
        checkbox = checkbox_label.find_element(By.XPATH, ".//input[@type='checkbox']")

        # Click the checkbox if it is not already checked
        if not checkbox.is_selected():
            checkbox.click()
            time.sleep(2)

    # Set a maximum number of attempts to click "Load More Results" button
    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:
        try:
            load_more_button = driver.find_element(By.XPATH, "//button[contains(@class, 'btn btn-sm btn-default')]//span[text()='Load More Results']")
            if load_more_button.is_displayed() and load_more_button.is_enabled():
                load_more_button.click()
                time.sleep(2)  # Sleep for 2 seconds to allow for results to load
                attempts += 1
            else:
                break
        except:
            break
    # Get the updated page content
    page_content = driver.page_source
    # Use Beautiful Soup to parse the updated HTML content
    soup = BeautifulSoup(page_content, "html.parser")
    # Find all camp item elements
    camp_elements = soup.select(".rec1-catalog-group-name.pull-left")
    camp_indices = list(range(len(camp_elements)))

    # Iterate over the indices to avoid stale element reference issues
    for index in camp_indices:
        # Re-locate the element before interacting with it
        camp_elements = driver.find_elements(By.CSS_SELECTOR, ".rec1-catalog-group-name.pull-left")
        if index < len(camp_elements):
            camp_element = camp_elements[index]
            if camp_element.is_displayed() and camp_element.is_enabled():
                camp_element.click()
                time.sleep(2)  # Sleep for 2 seconds to allow for any potential page updates

    page_content = driver.page_source
    # Use Beautiful Soup to parse the updated HTML content
    soup = BeautifulSoup(page_content, "html.parser")
    # Find all camp items using Beautiful Soup
    camp_elements = soup.select(".rec1-catalog-item")

    for camp_element in camp_elements:
        dates = camp_element.select_one(".rec1-catalog-item-feature.dates").get_text(strip=True)
        times = camp_element.select_one(".rec1-catalog-item-feature.times").get_text(strip=True)

        # Check if the camp matches the specified criteria
        if day_range in dates and time_range in times:
            print(f"Found matching camp: {camp_element.get_text(strip=True)}")

    # Get the updated page content
    page_content = driver.page_source

    # Use Beautiful Soup to parse the updated HTML content
    soup = BeautifulSoup(page_content, "html.parser")

    # Save the page content to an HTML file
    with open("updated_page.html", "w", encoding="utf-8") as file:
        file.write(page_content)
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the WebDriver
    driver.quit()
