from django.urls import path
from .views import parse_vlru

urlpatterns = [
    path('get_reviews/', parse_vlru, name='get-reviews'),
]