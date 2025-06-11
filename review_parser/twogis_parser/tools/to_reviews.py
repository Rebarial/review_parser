from datetime import datetime
from django.utils.timezone import make_aware
from common_parser.models import Review

def convert_2gis_reviews_to_model(branch, reviews_data):
    """
    Преобразует данные отзывов из 2GIS в объекты модели Review.
    
    :param branch: Объект Branch, к которому привязываются отзывы
    :param reviews_data: Словарь с данными отзывов из 2GIS API
    :return: Список объектов Review (не сохраненных в базу)
    """
    reviews_list = []
    
    for review_data in reviews_data.get('reviews', []):
        # Обработка даты
        try:
            published_date = make_aware(datetime.fromisoformat(review_data['date_created']))
        except (KeyError, ValueError):
            published_date = make_aware(datetime.now())
        
        # Получаем URL аватарки (берем самый большой доступный размер)
        avatar_url = ''
        photo_previews = review_data.get('user', {}).get('photo_preview_urls', {})
        if photo_previews:
            for size in ['1920x', '640x', '320x', '64x64', 'url']:
                if photo_previews.get(size):
                    avatar_url = photo_previews[size]
                    break
        
        # Создаем объект Review
        review = Review(
            branch=branch,
            author=review_data.get('user', {}).get('name', 'Аноним'),
            avatar=avatar_url if avatar_url else None,
            video=None, 
            photos=[],
            published_date=published_date,
            rating=review_data.get('rating', 5),
            content=review_data.get('text', ''),
            provider='2gis'
        )
        
        reviews_list.append(review)
    
        for review in reviews_list:
            review.save()

        return 200
    
