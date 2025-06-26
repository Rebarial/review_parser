from datetime import datetime
import requests
import re
from common_parser.tools.create_objects import create_video, get_or_create_playlist
from common_parser.tools.selenium_controle import selenium_get_driver

import time
import json

def get_token(url: str) -> dict:
    """Получаем токен анонимного пользователя из запросов на странице"""
    driver = selenium_get_driver(set_capability=True)

    driver.execute_cdp_cmd("Network.enable", {})

    requests_info = {}

    driver.get(url)
    time.sleep(5)

    logs = driver.get_log('performance')

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

                    result = json_data
                except:
                    print("Ответ не в JSON формате")
        except Exception as e:
            print(f"Не удалось получить тело ответа: {str(e)}")
    else:
        print("Запрос с 'get_anonym_token' не найден")

    driver.quit()

    return result


def parse_video_data(owner_id: int, album_id: int, token: str) -> dict:
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

def parse_playlist_data(owner_id: int, album_id: int, token:str) -> dict:
    params = {
        "owner_id": owner_id,
        "album_id": album_id,
        "access_token": token,
        "v": "5.199",
    }
    response = requests.get("https://api.vk.com/method/video.getAlbumById", params=params)
    return response.json()

def get_video_data(dict: dict, playlist: int, author: str)-> dict:
    """собираем видео для нашей модели"""
    scale = 0
    prew = ""
    for prew in dict.get('image'):
        width = int(prew.get('width'))
        if scale < width:
            scale = width
            prew = prew.get('url')
    
    print(prew)

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
    """из url получаем id автора и id плейлиста"""
    pattern = r'(-?\d+)_(\d+)$'
    match = re.search(pattern, url)

    if match:
        group1 = match.group(1) 
        group2 = match.group(2)  
        print(f"group1: {group1}, group2: {group2}")
        return (int(group1), int(group2))
    
    

def parse_vk_videos(url: str)-> tuple[int, int]:

    token = get_token(url).get("data", {}).get("access_token", "")

    if token:

        author_id, playlist_id = get_ids(url)

        videos = parse_video_data(author_id, playlist_id, token) 

        videos = videos.get("response")

        playlist = parse_playlist_data(author_id, playlist_id, token)

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
    else:
        raise ValueError("Ошибка: не удалось получить токен")

    return (len(videos), cnt)