import asyncio
from telethon import TelegramClient
import re
import os
import datetime
import logging
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from telethon import TelegramClient, sync
from PIL import Image
import io
import time

#holiwi
# Telethon setup
api_id = 21333990
api_hash = 'a5f8595bb23c197c06eb691adc870646'
phone_number = '+56995293023'
group_id = -1001812015314  # Replace with the actual group ID


# Selenium setup
chrome_profile_path = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Default"
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")
driver = webdriver.Chrome(options=chrome_options)



async def send_photo_message(client, task_number, screenshot_path):
    # Initialize the Telegram Client
    #client = TelegramClient(phone_number, api_id, api_hash)

    async with client:
        # Ensure the client is started and you are logged in
        await client.start()

        # Send the photo with a caption to the bot
        await client.send_file('@LinkedIn068', screenshot_path, caption=f"Tarea {task_number}")

def process_message(message):
    # Check if message is None or doesn't have a text attribute
    if message is None or not hasattr(message, 'text') or message.text is None:
        return False, None

    message_text = message.text
    type_1_match = re.match(r'Tarea (\w+)', message_text.split('\n')[0])
    if type_1_match:
        task_number = type_1_match.group(1)
        next_task_hour_match = re.search(r'Próxima tarea (\d{1,2}\.\d{2})', message_text)
        next_task_hour = next_task_hour_match.group(1).replace('.', ':') if next_task_hour_match else None
        link_match = re.search(r'https?://\S+', message_text)
        link = link_match.group(0) if link_match else None
        return True, (task_number, next_task_hour, link)

    return False, None


def calculate_delta(current_time, next_task_time_str):
    if next_task_time_str:
        next_task_time = current_time.replace(hour=int(next_task_time_str.split(':')[0]), minute=int(next_task_time_str.split(':')[1]))
        delta = next_task_time - current_time
    else:
        delta = datetime.timedelta(hours=1)
    
    return delta

def interact_with_instagram(driver, instagram_url):

    driver.get(instagram_url)

    try:
        like_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "xp7jhwk"))
        )
        like_button.click()
        time.sleep(5)  # Wait for interaction
        screenshot = driver.get_screenshot_as_png()
        screenshot = Image.open(io.BytesIO(screenshot))
        width, height = screenshot.size
        crop_area = (0, 0, int(width * 0.90), int(height * 0.75))
        cropped_screenshot = screenshot.crop(crop_area)
        cropped_screenshot.save("tarea.png")
        like_button.click()  # Click like button again to unlike
        time.sleep(5)
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error: {e}")

logging.basicConfig(level=logging.INFO)

async def fetch_messages():
    async with TelegramClient(phone_number, api_id, api_hash) as client:
        await client.start()
        logging.info("Telegram client started.")

        while True:
            try:
                if not client.is_connected():
                    logging.warning("Client disconnected. Attempting to reconnect...")
                    await client.connect()

                messages = await client.get_messages(group_id, limit=1)
                if messages:
                    message = messages[0]
                    message_time = message.date - datetime.timedelta(hours=3)
                    current_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)
                    is_recent = (current_time - message_time) < datetime.timedelta(minutes=20)
                    formatted_time = current_time.strftime('%H:%M')
                    random_seconds = random.randint(30, 720)
                    is_type_1, additional_info = process_message(message)
                    if is_type_1 and additional_info and is_recent:
                        task_number, next_task_hour, link = additional_info
                        delta = calculate_delta(message_time, next_task_hour)
                        if current_time.hour >= 22 or current_time.hour < 9:
                            delta2 = datetime.timedelta(hours=1)
                        else:
                            delta2 = calculate_delta(current_time, next_task_hour)
                        print("-----")
                        print(formatted_time, "   ", delta2)
                        print("-----")
                        if link:
                            interact_with_instagram(driver, link)
                            time.sleep(random_seconds)
                            await send_photo_message(client, task_number, "C:\\code\\TelegramAntiEstafasBot\\tarea.png")
                            
                            if random_seconds > int(delta2.total_seconds()):
                                delta2 = datetime.timedelta(hours=0)
                            else:
                                delta2 = delta2 - datetime.timedelta(seconds=random_seconds)
                        #driver.close()
                        #await asyncio.sleep(20)
                        
                        print("-----")
                        print(formatted_time, "   ", delta2, " post restas")
                        print("-----")
                        await asyncio.sleep(delta2.total_seconds())
                    else:
                        if current_time.hour >= 22 or current_time.hour < 9:
                            print("-----")
                            print(formatted_time, " 1 hour")
                            print("-----")
                            await asyncio.sleep(3600)

                        else:
                            print("-----")
                            print(formatted_time, " 1 minuto")
                            print("-----")
                            #driver.close()
                            await asyncio.sleep(60)

            except ConnectionError as e:
                logging.error(f"ConnectionError encountered: {e}")
                # Handle reconnection here
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                # Handle other exceptions
            finally:
                # This can be used for cleanup or final checks
                pass

asyncio.run(fetch_messages())