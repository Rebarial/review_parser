from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from typing import Optional
import re
from common_parser.tools.create_objects import get_or_create_Branch, get_or_create_Organization, create_review
from common_parser.tools.parse_date_string import parse_date_string
from loguru import logger
from datetime import datetime

logger.add("debug.log", enqueue=True, format="{time} {level} {message}", level="DEBUG")

@logger.catch
def parse(url:str, limit:Optional[int] = None) -> list[dict]:
    options = Options()
    options.add_argument('--headless')  
    options.add_argument('--no-sandbox')   
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(
      service=Service(ChromeDriverManager().install()),
      options=options
    )
    result = []
    

    driver.get(url)
    wait = WebDriverWait(driver, 20)

    time.sleep(3)

    reviews_counter = -1
    raiting_global = -1
    reviews_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.tabs-select-view__title._name_reviews')))
    if reviews_tab:
        reviews_counter = reviews_tab.find_element(By.CLASS_NAME, 'tabs-select-view__counter').text
    try:
        stars_block = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.business-card-title-view__header')))
    except Exception as e:
        stars_block = None
        print(f"Элемент не найден: {e}")

    if stars_block:
        raiting_global = float(stars_block.find_element(By.CSS_SELECTOR, '.business-rating-badge-view__rating-text').text.replace(",", "."))
    
    time.sleep(3)
    # Переключаемся на вкладку "Отзывы"
    driver.execute_script("arguments[0].click();", reviews_tab)
    #reviews_tab.click()

    time.sleep(3)

    scroll = driver.find_element(By.CSS_SELECTOR, '.scroll__container')

    last_height = driver.execute_script('return arguments[0].scrollHeight;', scroll)

    max_scroll_attempts = 10

    scroll_count = 0

    while True:
        driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', scroll)

        time.sleep(3)
        
        new_height = driver.execute_script('return arguments[0].scrollHeight;', scroll)
        
        if new_height == last_height or scroll_count >= max_scroll_attempts:
            break
            
        last_height = new_height
        scroll_count += 1
    try:
        review_blocks = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.business-review-view__info')))
    except:
        review_blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='business-review-view__info']")))

    count = 0
    
    for review_block in review_blocks:
            
            avatar_img_url = review_block.find_element(By.CSS_SELECTOR, '.user-icon-view__icon')
            style_attr = avatar_img_url.get_attribute('style')
            match = match = re.search(r'url\(["\']?(.*?)["\']?\)', style_attr)

            if match:
                avatar_img_url = match.group(1).strip('"')
            else:
                avatar_img_url = ""

            author_name = review_block.find_element(By.CSS_SELECTOR, '.business-review-view__author-name').text.strip()
        
            date_published = review_block.find_element(By.CSS_SELECTOR, '.business-review-view__date').text.strip()

            photos_obj = review_block.find_elements(By.CSS_SELECTOR, '.business-review-media__item-img')

            image_srcs = []
            for photo in photos_obj:
                image_srcs.append(photo.get_attribute('src'))

            # Записываем их через запятую
            photos = ', '.join(image_srcs)
        
            stars_count = len(review_block.find_elements(By.CSS_SELECTOR, '.business-rating-badge-view__star._full'))
        
            review_text = review_block.find_element(By.CSS_SELECTOR, '.business-review-view__body').text.strip()

            try:
                result.append(
                    {
                        'author': author_name,
                        'avatar': avatar_img_url,
                        'published_date': parse_date_string(date_published),
                        'rating': stars_count,
                        'content': review_text,
                        'provider': 'yandex',
                        'photos': photos
                    }
                )
                count += 1
            except Exception:
                print("Ошибка при добавлении ", Exception)
            if limit and limit == count:
                break
    driver.quit()
    return {        
            'count': reviews_counter,
            'rating': raiting_global,
            'reviews': result,
         }

def create_yandex_reviews(url: str, inn: str, org_name: str ="", address: str ="", count: str = 50) -> int:
    dict_yandex = parse(url)

    if not dict_yandex:
        dict_yandex = parse(url)
        
    print(dict_yandex)

    branch = get_or_create_Branch(
        organization=get_or_create_Organization(inn, org_name),
        address=address,
        url_name="yandex_map_url",
        url=url,
        review_count_name="yandex_review_count",
        review_count=dict_yandex['count'],
        review_avg_name="yandex_review_avg",
        review_avg=dict_yandex['rating'],
    )

    branch.yandex_parse_date = datetime.now()
    branch.save()

    for d in dict_yandex['reviews']:
        d['branch'] = branch   

    cnt = 0

    for review in dict_yandex['reviews']:
        if create_review(review):
            cnt += 1

    return cnt