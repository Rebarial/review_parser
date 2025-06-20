from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common_parser.tools.selenium_controle import selenium_get_driver, wait_time, max_scrolls
import time
from typing import Optional
import re
from common_parser.tools.create_objects import get_or_create_Branch, get_or_create_Organization, create_review
from common_parser.tools.parse_date_string import parse_date_string
from loguru import logger
from datetime import datetime
from dateutil.relativedelta import relativedelta

logger.add("debug.log", enqueue=True, format="{time} {level} {message}", level="DEBUG")

def google_date_parse(data):
    current_date = datetime.now()
    result_dates = None

    date_str = data
    if 'месяц' in date_str:
        try:
            months_ago = int(date_str.split()[0])
        except:
            months_ago = 1
        result_dates = (current_date - relativedelta(months=months_ago))
    elif 'лет' in date_str or 'год' in date_str:
        try:
            years_ago = int(date_str.split()[0])
        except:
            years_ago = 1
        result_dates = (current_date - relativedelta(years=years_ago))
    elif 'недел' in date_str:
        try:
            weeks_ago = int(date_str.split()[0])
        except:
            weeks_ago = 1
        result_dates = (current_date - relativedelta(weeks=weeks_ago))
    return result_dates

@logger.catch
def parse(url:str, limit:Optional[int] = None) -> list[dict]:
    driver = selenium_get_driver()
    result = []

    driver.get(url)
    wait = WebDriverWait(driver, wait_time)

    time.sleep(3)

    reviews_counter = -1
    raiting_global = -1
    reviews_tab = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".EIgkw"))
    )
    menu = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.hh2c6')))
    for el in menu:
        if el.text == "Отзывы" or el.text == "Reviews":
            reviews_tab = el

    time.sleep(3)

    reviews_counter = int(wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.F7nice'))).text.split('(')[1].split(')')[0])

    try:
        stars_block = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.F7nice')))
    except Exception as e:
        stars_block = None
        print(f"Элемент не найден: {e}")

    if stars_block:
        raiting_global = float(stars_block.find_element(By.XPATH, ".//span[@aria-hidden='true']").text.replace(",", "."))
    
    time.sleep(3)
    # Переключаемся на вкладку "Отзывы"
    driver.execute_script("arguments[0].click();", reviews_tab)
    #reviews_tab.click()

    time.sleep(3)

    scroll = driver.find_element(By.CSS_SELECTOR, '.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde')

    last_height = driver.execute_script('return arguments[0].scrollHeight;', scroll)

    max_scroll_attempts = max_scrolls

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
        review_blocks = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.jftiEf.fontBodyMedium')))
    except:
        review_blocks = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='jftiEf.fontBodyMedium']")))

    count = 0
    
    for review_block in review_blocks:
            
            avatar_img_url = review_block.find_element(By.CSS_SELECTOR, '.NBa7we')
            style_attr = avatar_img_url.get_attribute('src')
            #match = match = re.search(r'url\(["\']?(.*?)["\']?\)', style_attr)

            if style_attr:
                avatar_img_url = style_attr
            else:
                avatar_img_url = ""

            author_name = review_block.find_element(By.CSS_SELECTOR, '.d4r55').text.strip()
        
            date_published = review_block.find_element(By.CSS_SELECTOR, '.rsqaWe').text.strip()

            photos_obj = review_block.find_elements(By.CSS_SELECTOR, '.Tya61d')

            image_srcs = []
            for photo in photos_obj:
                style_attr = photo.get_attribute('style')
                try:
                    image_srcs.append(style_attr.split("\"")[1])
                except Exception:
                    print(Exception)

            # Если хотите оставить пустые строки для отсутствующих изображений
            photos = ', '.join(image_srcs)
            try:
                stars_count = len(review_block.find_elements(By.CSS_SELECTOR, '.elGi1d'))
            except:
                stars_count = -1
            
            #review_text = review_block.find_element(By.CSS_SELECTOR, '.GHT2ce')
            try:
                review_text = review_block.find_element(By.XPATH, '//div[@class="MyEned"]').text
            except:
                review_text = ""
            
            try:
                result.append(
                    {
                        'author': author_name,
                        'avatar': avatar_img_url,
                        'published_date': google_date_parse(date_published),#parse_date_string(date_published),
                        'rating': stars_count,
                        'content': review_text,
                        'provider': 'google',
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

#print(parse("https://www.google.ru/maps/place/Чистота-ДВ/@46.9502546,142.721615,15.25z/data=!4m16!1m9!3m8!1s0x5f19aa109dbb4ad7:0x30530b3bed326005!2z0KfQuNGB0YLQvtGC0LAt0JTQkg!8m2!3d46.9506031!4d142.7240417!9m1!1b1!16s%2Fg%2F12qgnj0dr!3m5!1s0x5f19aa109dbb4ad7:0x30530b3bed326005!8m2!3d46.9506031!4d142.7240417!16s%2Fg%2F12qgnj0dr?entry=ttu&g_ep=EgoyMDI1MDYxNS4wIKXMDSoASAFQAw%3D%3D"))

def create_google_reviews(url: str, inn: str, org_name: str ="", address: str ="", count: str = 50) -> int:
    dict_google = parse(url)

    branch = get_or_create_Branch(
        organization=get_or_create_Organization(inn, org_name),
        address=address,
        url_name="google_map_url",
        url=url,
        review_count_name="google_review_count",
        review_count=dict_google['count'],
        review_avg_name="google_review_avg",
        review_avg=dict_google['rating'],
    )

    branch.google_parse_date = datetime.now()
    branch.save()

    for d in dict_google['reviews']:
        d['branch'] = branch   

    cnt = 0

    for review in dict_google['reviews']:
        if create_review(review):
            cnt += 1

    return cnt