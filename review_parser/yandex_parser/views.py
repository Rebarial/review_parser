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
from yandex_parser.tools.parser import parse

class FillReviewsAPI(APIView):
    """ Представление для отправки данных организаций и филиалов вместе с отзывами. """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'inn': openapi.Schema(type=openapi.TYPE_STRING, description="ИНН организации"),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description="Название организации (опционально)"),
                'address': openapi.Schema(type=openapi.TYPE_STRING, description="Адрес (опционально)"),
                'link': openapi.Schema(type=openapi.TYPE_STRING, description="Ссылка на Яндекс.Карту"),
                'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Количество (опционально)"),
                
            },
            required=["inn", "link"] 
        ),
        responses={201: "Объекты успешно созданы", 400: "Некорректные данные"}
    )
    def post(self, request):
        data = request.data
        inn = data.get('inn')
        name = data.get('name')
        link = data.get('link')
        count = data.get('count')
        address = data.get('address') 

        # Проверяем существование организации по ИНН
        try:
            organization = Organization.objects.get(inn=inn)
        except Organization.DoesNotExist:
            serializer_org = OrganizationSerializer(data={
                "inn": inn,
                "title": name or ""
                })
            if serializer_org.is_valid():
                organization = serializer_org.save()
            else:
                return Response({'errors': serializer_org.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем наличие филиала по ссылке
        try:
            branch = Branch.objects.get(yandex_map_link=link, organization=organization)
        except Branch.DoesNotExist:
            serializer_branch = BranchSerializer(data={
                'organization': organization.id,
                'address': address or "",
                'yandex_map_link': link
            })
            if serializer_branch.is_valid():
                branch = serializer_branch.save()
            else:
                return Response({'errors': serializer_branch.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Парсим отзывы и добавляем новые
        parsed_reviews = []
        reviews_list = parse(link, count or None)

        for review_item in reviews_list:
            pub_date = parse_date_string(review_item["date"])
            
            existing_review = Review.objects.filter(
                branch=branch,
                author=review_item["author"],
                published_date=pub_date
            ).exists()

            if not existing_review:
                serializer_review = ReviewSerializer(data={
                    'branch': branch.id,
                    'author': review_item["author"],
                    'avatar': review_item["avatar"] or "",
                    'rating': review_item["rating"],
                    'content': review_item["content"],
                    'published_date': pub_date
                })
                
                if serializer_review.is_valid():
                    serializer_review.save()
                    parsed_reviews.append(serializer_review.validated_data)
                else:
                    return Response({'errors': serializer_review.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': f'Отзывов создано: {len(parsed_reviews)}'
        }, status=status.HTTP_201_CREATED)