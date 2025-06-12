from datetime import datetime
from common_parser.models import Branch

def convert_2gis_reviews_to_model_data(branch: Branch, review_data: dict) -> dict:
    """
    Преобразует данные отзывов из 2GIS в объекты модели Review.
    
    :param branch: Объект Branch, к которому привязываются отзывы
    :param review_data: Данные review
    :return: словарь для модели review
    """
   
    try:
        published_date = datetime.fromisoformat(review_data['date_created'])
    except (KeyError, ValueError):
        published_date = datetime.now()
    
    avatar_url = review_data.get('user', {}).get('photo_preview_urls', {}).get('url', '')
    
    review = {
        'branch': branch,
        'author': review_data.get('user', {}).get('name', 'Аноним'),
        'avatar': avatar_url if avatar_url else None,
        'video': None, 
        'photos': [],
        'published_date': published_date,
        'rating': review_data.get('rating', 5),
        'content': review_data.get('text', ''),
        'provider': '2gis'
    }
    return review
    
