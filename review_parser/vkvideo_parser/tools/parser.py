from dotenv import load_dotenv
import os
from datetime import datetime
import requests
import re
from common_parser.tools.create_objects import create_video, get_or_create_playlist

load_dotenv()

API_KEY = "vk1.a.oCjIYSm917BvsFoTOsjYRorWyFNkmWMy2X-3HPbr8W3NmTtRK_mvw9tKZYYhVwLPtWqS9ZdVw44NylSj-9dgth8oLsNzGPcOmqxcK4Mg9P6as0BHvFS4u5VrFGSIWL3zTDLM1pcF3lP2PKrsGo7CehCm7r64pXZjrq5a-WgZB7C9s87EPtWRfgAZRZLXFzEj"#os.getenv("VKVIDEO_API_KEY")


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def get_token():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    # Включаем логирование сети
    driver.execute_cdp_cmd("Network.enable", {})

    # Создаем список для хранения информации о запросах
    requests_info = {}

    # Открываем страницу
    driver.get("https://vkvideo.ru/@winline/playlists")
    time.sleep(5)  # Ждем загрузки

    # Получаем логи производительности
    logs = driver.get_log('performance')

    # Ищем нужный запрос
    target_request_id = None
    target_url = None

    for entry in logs:
        try:
            log = json.loads(entry['message'])
            message = log.get('message', {})
            params = message.get('params', {})
            request = params.get('request', {})
            url = request.get('url', '')
            
            if 'get_anonym_token' in url:
                target_request_id = params.get('requestId')
                target_url = url
                break
        except:
            continue

    result = ""
    if target_request_id:
        try:
            response = driver.execute_cdp_cmd(
                "Network.getResponseBody",
                {"requestId": target_request_id}
            )
            
            if 'body' in response:
                try:
                    json_data = json.loads(response['body'])
                    #print("Распарсенный JSON:")
                    result = json_data#json.dumps(json_data, indent=2, ensure_ascii=False)
                except:
                    print("Ответ не в JSON формате")
        except Exception as e:
            print(f"Не удалось получить тело ответа: {str(e)}")
    else:
        print("Запрос с 'get_anonym_token' не найден")

    driver.quit()

    return result


def parse_video_data(owner_id, album_id, token):
    params = {
        "owner_id": owner_id,
        "album_id": album_id,
        "access_token": token,
        "v": "5.199",
        "count": 10,
        "extended": 1
    }
    response = requests.get("https://api.vk.com/method/video.get", params=params)
    return response.json()

def parse_playlist_data(owner_id, album_id, token):
    params = {
        "owner_id": owner_id,
        "album_id": album_id,
        "access_token": token,
        "v": "5.199",
    }
    response = requests.get("https://api.vk.com/method/video.getAlbumById", params=params)
    return response.json()

def get_video_data(dict, playlist, author)-> dict:

    scale = 0
    prew = ""
    for prew in dict.get('image'):
        width = int(prew.get('width'))
        if scale < width:
            scale = width
            prew = prew.get('url')
                       

    result = {
        'url': dict.get('share_url'),
        'title': dict.get('title'),
        'author': author,
        'date': datetime.fromtimestamp(dict.get('date')),
        'preview': prew,
        'duration': dict.get('duration'),
        'playlist': playlist,
    }

    return result

def get_ids(url: str) -> tuple[int, int]:

    pattern = r'(-?\d+)_(\d+)$'
    match = re.search(pattern, url)

    if match:
        group1 = match.group(1) 
        group2 = match.group(2)  
        print(f"group1: {group1}, group2: {group2}")
        return (int(group1), int(group2))
    
    

def parse_vk_videos(url: str)-> None:

    tok = get_token().get("data").get("access_token")
    #print(tok.get("data").get("access_token"))

    author_id, playlist_id = get_ids(url)

    videos = parse_video_data(author_id, playlist_id, tok) 

    videos = videos.get("response")

    playlist = parse_playlist_data(author_id, playlist_id, tok)

    playlist = playlist.get("response")

    playlist_data = {
        'title': playlist.get('title'),
        'count': playlist.get("count"),
        'url': url,
        'parse_date': datetime.now(),
        'provider': 'vk'

    }

    playlist = get_or_create_playlist(playlist_data)

    cnt = 0

    author = videos.get('groups')[0].get("name")
    for video in videos.get('items'):
        if create_video(get_video_data(video, playlist.id,author)):
            cnt += 1

    return (len(videos), cnt)