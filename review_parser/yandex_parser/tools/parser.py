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
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 40)

        # Переключаемся на вкладку "Отзывы"
        reviews_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.tabs-select-view__title._name_reviews')))
        reviews_tab.click()

        time.sleep(3)

        scroll = driver.find_element(By.CSS_SELECTOR, '.scroll__container')

        last_height = driver.execute_script('return arguments[0].scrollHeight;', scroll)

        max_scroll_attempts = 10

        scrill = 0

        while True:
            driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', scroll)

            time.sleep(3)
            
            new_height = driver.execute_script('return arguments[0].scrollHeight;', scroll)
            
            if new_height == last_height or scroll >= max_scroll_attempts:
                break
                
            last_height = new_height
            scroll += 1

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
