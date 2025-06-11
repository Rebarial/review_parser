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




print(parse('https://public-api.reviews.2gis.com/2.0/branches/70000001080371174/reviews?limit=50&is_advertiser=true&fields=meta.branch_rating,meta.branch_reviews_count,meta.total_count&without_my_first_review=false&rated=true&sort_by=date_edited&key=37c04fe6-a560-4549-b459-02309cf643ad&locale=ru_RU'))