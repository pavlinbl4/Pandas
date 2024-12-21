"""
Функция принимает photo_id и путь к сохраняемому файлу (так как файл может сохраняться
под другим именем
"""

import os

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from must_have.crome_options import setting_chrome_options

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=setting_chrome_options())


def download_photo_preview_by_id(photo_id: str, picture_folder_downloads, image_file_name=None):
    image_file_name = image_file_name if image_file_name else f"{photo_id}.jpg"

    image_path = os.path.join(picture_folder_downloads, image_file_name)
    os.makedirs(picture_folder_downloads, exist_ok=True)

    driver.get(f'https://www.tassphoto.com/ru/asset/fullTextSearch/search/{photo_id}/page/1')
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.ID, "userrequest"))
    )

    picture_element = driver.find_element(By.CSS_SELECTOR, f"img.thumb{photo_id}")
    picture_url = picture_element.get_attribute("src")

    image_response = requests.get(picture_url)

    with open(image_path, 'wb') as img_file:
        img_file.write(image_response.content)
