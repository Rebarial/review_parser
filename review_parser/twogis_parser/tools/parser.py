import requests
import time
import json

def parse(url):
    response = requests.get(url)

    if response.status_code != 200:
        time.sleep(30)

        response = requests.get(url)

    response_text = response.text
    response_dict = json.loads(response_text)

    if response_dict["meta"]["total_count"] == 0:
        time.sleep(30)
        response = requests.get(url)
        response_text = response.text
        response_dict = json.loads(response_text)

    if response_dict["meta"]["total_count"] == 0:
        return {'error': 'parse failed'}
    
    response_dict

    return {
        'branch_rating': response_dict["meta"]["branch_rating"],
        'total': response_dict["meta"]["total_count"],
        'reviews': response_dict["reviews"]
    }
