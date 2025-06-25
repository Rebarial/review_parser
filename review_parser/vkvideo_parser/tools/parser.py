from dotenv import load_dotenv
import os
from datetime import datetime
import requests
import re
from common_parser.tools.create_objects import create_video, get_or_create_playlist

load_dotenv()

API_KEY = os.getenv("VKVIDEO_API_KEY")


def parse_video_data(owner_id, album_id):
    params = {
        "owner_id": owner_id,
        "album_id": album_id,
        "access_token": API_KEY,
        "v": "5.199",
        "count": 10,
        "extended": 1
    }
    response = requests.get("https://api.vk.com/method/video.get", params=params)
    return response.json()

def parse_playlist_data(owner_id, album_id):
    params = {
        "owner_id": owner_id,
        "album_id": album_id,
        "access_token": API_KEY,
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

    author_id, playlist_id = get_ids(url)

    videos = parse_video_data(author_id, playlist_id).get("response")

    playlist = parse_playlist_data(author_id, playlist_id).get("response")

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