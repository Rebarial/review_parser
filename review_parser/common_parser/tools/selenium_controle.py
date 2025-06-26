
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome

wait_time = 10
max_scrolls = 5

def selenium_get_driver(set_capability = False):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=40,1080')
    if set_capability:
      chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    return Chrome(
      service=Service(ChromeDriverManager().install()),
      options=chrome_options
    )