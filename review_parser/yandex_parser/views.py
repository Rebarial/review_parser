from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from common_parser.serializers import OrganizationSerializer, BranchSerializer, ReviewSerializer
from common_parser.models import Organization, Branch, Review
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from common_parser.tools.parse_date_string import parse_date_string
from yandex_parser.tools.parser import parse, create_yandex_reviews
from rest_framework.decorators import api_view

@swagger_auto_schema(
    method='POST',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'inn': openapi.Schema(type=openapi.TYPE_STRING, description="ИНН организации"),
            'org_name': openapi.Schema(type=openapi.TYPE_STRING, description="Название организации (опционально)"),
            'address': openapi.Schema(type=openapi.TYPE_STRING, description="Адрес (опционально)"),
            'url': openapi.Schema(type=openapi.TYPE_STRING, description="Ссылка на Яндекс.Карту"),
            'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Количество (опционально)"),
            
        },
        required=["inn", "url"] 
    ),
    responses={201: "Объекты успешно созданы", 400: "Некорректные данные"}
)
@api_view(['POST'])
def parse_yandex(request):
    data = request.data
    inn = data.get('inn')
    org_name = data.get('org_name')
    address = data.get('address')
    url = data.get('url')
    count = data.get('count')   

    cnt = create_yandex_reviews(
        inn=inn,
        org_name=org_name,
        address=address,
        url=url,
       count=count
    )

    return Response({
            'message': f'Отзывов создано: {cnt}'
        }, status=status.HTTP_201_CREATED)
