from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from typing import Optional
import re

def parse(url:str, limit:Optional[int] = None) -> list[dict]:
    driver = webdriver.Chrome()
    result = []
    driver.get('https://yandex.ru/maps/75/vladivostok/?ll=131.908412%2C43.092887&mode=poi&poi%5Bpoint%5D=131.909558%2C43.093373&poi%5Buri%5D=ymapsbm1%3A%2F%2Forg%3Foid%3D107198066732&z=17.24')
    try:
        wait = WebDriverWait(driver, 20)

        # Переключаемся на вкладку "Отзывы"
        reviews_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.tabs-select-view__title._name_reviews')))
        reviews_tab.click()

        time.sleep(3)

        scroll = driver.find_element(By.CSS_SELECTOR, '.scroll__container')

        last_height = driver.execute_script('return arguments[0].scrollHeight;', scroll)

        while True:
            driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', scroll)

            time.sleep(3)
            
            new_height = driver.execute_script('return arguments[0].scrollHeight;', scroll)
            
            if new_height == last_height:
                break
                
            last_height = new_height

        review_blocks = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.business-review-view__info')))
        count = 0
        
        
        for review_block in review_blocks:
            try:
                avatar_img_url = review_block.find_element(By.CSS_SELECTOR, '.user-icon-view__icon')
                style_attr = avatar_img_url.get_attribute('style')
                match = match = re.search(r'url\(["\']?(.*?)["\']?\)', style_attr)

                if match:
                    avatar_img_url = match.group(1).strip('"')
                else:
                    avatar_img_url = ""

                author_name = review_block.find_element(By.CSS_SELECTOR, '.business-review-view__author-name').text.strip()
            
                date_published = review_block.find_element(By.CSS_SELECTOR, '.business-review-view__date').text.strip()
            
                stars_count = len(review_block.find_elements(By.CSS_SELECTOR, '.business-rating-badge-view__star._full'))
            
                review_text = review_block.find_element(By.CSS_SELECTOR, '.business-review-view__body-text').text.strip()

                result.append(
                    {
                        'author': author_name,
                        'avatar': avatar_img_url,
                        'date': date_published,
                        'rating': stars_count,
                        'content': review_text
                    }
                )
                count += 1
                if limit and limit == count:
                    break
            except Exception as e:
                print(f"Произошла ошибка при обработке отзыва: {e}")
        print("Count: ",count)
    except Exception as e:
        print(f"Произошла ошибка при парсинге: {e}")
    finally:
        driver.quit()
    return result
