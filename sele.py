from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from PIL import Image
import io
import time

chrome_profile_path = r"C:\Users\dpv_2\AppData\Local\Google\Chrome\User Data\Default"
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")
driver = webdriver.Chrome(options=chrome_options)

# Read the last message from the text file
with open("last_message.txt", "r", encoding='utf-8') as file:
    lines = file.readlines()

# Extract the URL (assuming it's the last line)
instagram_url = lines[-1].strip()

# Open the URL
driver.get(instagram_url)

# Wait for the like button to be clickable
try:
    like_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "xp7jhwk"))
    )
    like_button.click()
except TimeoutException:
    print("Timed out waiting for the like button to load")
except NoSuchElementException:
    print("Could not find the like button")

# Wait for a while to observe interactions (optional, for testing)
time.sleep(1)

# Take a screenshot of the entire page
screenshot = driver.get_screenshot_as_png()
screenshot = Image.open(io.BytesIO(screenshot))

# Calculate dimensions for cropping (70% of the width and height)
width, height = screenshot.size
crop_area = (0, 0, int(width * 0.90), int(height * 0.75))

# Crop and save the screenshot
cropped_screenshot = screenshot.crop(crop_area)
cropped_screenshot.save("tarea.png")

# When done, close the browser
driver.quit()
