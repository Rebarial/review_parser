import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def parse_vlru_reviews(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    reviews_list = soup.find('ul', {'id': 'CommentsList'})
    
    if not reviews_list:
        return []
    
    reviews = []
    
    for review_item in reviews_list.find_all('li', recursive=False):
        try:
            comment_id = review_item.get('comment')
            profile_id = review_item.get('data-profile-id')
            review_type = review_item.get('data-type')
            timestamp = int(review_item.get('data-timestamp'))
            published_date = datetime.fromtimestamp(timestamp)
            
            author_block = review_item.find('span', class_='user-name')
            author = author_block.get_text(strip=True) if author_block else "Anonymous"
            
            # Extract avatar
            avatar_img = review_item.find('img', class_='avatar')
            avatar = avatar_img['src'] if avatar_img else None
            
            # Extract rating
            rating = 0
            rating_wrapper = review_item.find('div', class_='cmt-rating-wrapper')
            if rating_wrapper:
                active_rating = rating_wrapper.find('div', class_='active')
                if active_rating and 'data-value' in active_rating.attrs:
                    rating = int(active_rating['data-value'])
                    rating *= 5
            
            # Extract content
            comment_text = review_item.find('p', class_='comment-text')
            content = comment_text.get_text(strip=True) if comment_text else ""
            
            # Extract likes count
            likes_block = review_item.find('span', class_='likes')
            likes_count = int(likes_block.get('data-like-count', 0)) if likes_block else 0
            
            # Create review dictionary
            review = {
                'author': author,
                'avatar': avatar,
                'video': None, 
                'photos': [],  
                'published_date': published_date,
                'rating': rating,
                'content': content,
                'provider': 'vlru',
                'external_id': comment_id,
                'likes_count': likes_count,
                'profile_id': profile_id
            }
            
            reviews.append(review)
            
        except Exception as e:
            print(f"Error parsing review: {e}")
            continue
    
    return reviews


def parse(url):
    url = 'https://www.vl.ru/commentsgate/ajax/thread/company/it-solutions/embedded'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.vl.ru/it-solutions'
    }
    params = {'theme': 'company', 'moderatorMode': '1'}

    response = requests.get(url, headers=headers, params=params)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        print(data)


def get_company_from_url(url: str) -> str:
    match = re.search(r'/([^/]+)$', url)
    if match:
        return match.group(1)
    return None


print(get_company_from_url('https://www.vl.ru/it-solutions'))