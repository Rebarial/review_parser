from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from vl_parser.tools.parser import create_vlru_reviews
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from .models import Branch, Review, BranchIPMapping
import json
from rest_framework import serializers
from .serializers import ReviewSerializer, BranchSerializer
from django.db.models import Count

class ProviderSerializer(serializers.Serializer):
    provider = serializers.CharField()
    count = serializers.IntegerField()


@swagger_auto_schema(
    method="GET",
    manual_parameters=[
        openapi.Parameter('branch_id', openapi.IN_QUERY, description="Идентификатор филиала", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('providers', openapi.IN_QUERY,
                  description="Список провайдеров",
                  type=openapi.TYPE_ARRAY,
                  items=openapi.Schema(
                      type=openapi.TYPE_OBJECT,
                      properties={
                          'provider': openapi.Schema(type=openapi.TYPE_STRING, title="Название провайдера"),
                          'count': openapi.Schema(type=openapi.TYPE_INTEGER, title="Количество записей")
                      },),
                  required=False),
    ],
    responses={200: '''
                        "branch": {
                            "id",
                            "address",
                            "yandex_map_url",
                            "twogis_map_url",
                            "vlru_url",
                            "twogis_review_count",
                            "twogis_review_avg",
                            "vlru_review_count",
                            "vlru_review_avg",
                            "organization"
                        },
                        'provider_reviews_count': [
                            {
                                "provider",
                                "review_count"
                            }
                        ]
                        "reviews": [
                            {
                                "id",
                                "author",
                                "avatar",
                                "video",
                                "photos",
                                "published_date",
                                "rating",
                                "content",
                                "provider",
                                "branch"
                            },
                        ]
                                ''', 400: "Некорректные данные"}
)
@api_view(['GET'])
def get_reviews(request):
    branch_id = request.query_params.get('branch_id')
    providers = request.query_params.get('providers')
    if providers:
        providers = "[" + providers + "]"

    if not branch_id:
        pass

    branch = Branch.objects.get(id = branch_id)

    reviews_data = []
    if providers:
        providers = json.loads(providers)
        print(providers)
        for prov in providers:
            print(prov)
            if prov["count"]:
                reviews_data += ReviewSerializer(Review.objects.filter(branch=branch, provider=prov["provider"]).order_by('published_date')[:prov["count"]], many=True).data
            else:
                reviews_data += ReviewSerializer(Review.objects.filter(branch=branch, provider=prov["provider"]).order_by('published_date'), many=True).data
 
            
    else:
        reviews = Review.objects.filter(branch=branch)
        reviews_serializer = ReviewSerializer(reviews, many=True)
        reviews_data = reviews_serializer.data


    branch_serializer = BranchSerializer(branch)

    data = {         
            'branch': branch_serializer.data,
            'provider_reviews_count' : Review.objects.filter(branch=branch).values('provider').annotate(review_count=Count('id')),
            'reviews': reviews_data,
            }
    
    return Response(data)


@swagger_auto_schema(
    method="GET",
        manual_parameters=[
        openapi.Parameter('providers', openapi.IN_QUERY,
                  description="Список провайдеров",
                  type=openapi.TYPE_ARRAY,
                  items=openapi.Schema(
                      type=openapi.TYPE_OBJECT,
                      properties={
                          'provider': openapi.Schema(type=openapi.TYPE_STRING, title="Название провайдера"),
                          'count': openapi.Schema(type=openapi.TYPE_INTEGER, title="Количество записей")
                      },),
                  required=False),
    ],
        responses={200: '''
                        "ip",
                        "branch": [{
                            "id",
                            "address",
                            "yandex_map_url",
                            "twogis_map_url",
                            "vlru_url",
                            "twogis_review_count",
                            "twogis_review_avg",
                            "vlru_review_count",
                            "vlru_review_avg",
                            "organization"
                        }],
                        'provider_reviews_count': [
                            {
                                "provider",
                                "review_count"
                            }
                        ]
                        "reviews": [
                            {
                                "id",
                                "author",
                                "avatar",
                                "video",
                                "photos",
                                "published_date",
                                "rating",
                                "content",
                                "provider",
                                "branch"
                            },
                        ]
                                ''', 400: "Некорректные данные"}
)
@api_view(['GET'])
def get_reviews_by_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    objects_with_ip = BranchIPMapping.objects.filter(ip_address=ip)
    branches = []
    for mapping in objects_with_ip:
        branches.append(mapping.branch)

    providers = request.query_params.get('providers')
    if providers:
        providers = "[" + providers + "]"

    reviews_data = []
    if providers:
        providers = json.loads(providers)
        print(providers)
        for prov in providers:
            print(prov)
            if prov["count"]:
                reviews_data += ReviewSerializer(Review.objects.filter(branch__in=branches, provider=prov["provider"]).order_by('published_date')[:prov["count"]], many=True).data
            else:
                reviews_data += ReviewSerializer(Review.objects.filter(branch__in=branches, provider=prov["provider"]).order_by('published_date'), many=True).data
 
            
    else:
        reviews = Review.objects.filter(branch__in=branches)
        reviews_serializer = ReviewSerializer(reviews, many=True)
        reviews_data = reviews_serializer.data

    branch_serializer = BranchSerializer(branches, many=True)

    data = {
            'ip': ip,
            'branches': branch_serializer.data,
            'provider_reviews_count' : Review.objects.filter(branch__in=branches).values('provider').annotate(review_count=Count('id')),
            'reviews': reviews_data,
            }
    
    return Response(data)