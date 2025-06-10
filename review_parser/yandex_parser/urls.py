from django.urls import path
from .views import FillReviewsAPI

urlpatterns = [
    path('fill/', FillReviewsAPI.as_view(), name='fill-yandex'),
]