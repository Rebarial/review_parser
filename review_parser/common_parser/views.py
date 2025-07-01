from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from vl_parser.tools.parser import create_vlru_reviews
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from .models import Branch, Review, BranchIPMapping, PlaylistIPMapping, Video, Playlist
import json
from rest_framework import serializers
from .serializers import ReviewSerializer, BranchSerializer, VideoSerializer, PlaylistSerializer
from django.db.models import Count, Q

class ProviderSerializer(serializers.Serializer):
    provider = serializers.CharField()
    count = serializers.IntegerField()

PROVIDER_CHOICES = [
    'yandex',
    'google',
    '2gis',
    'vlru'
]

@swagger_auto_schema(
    method="GET",
    manual_parameters=[
        openapi.Parameter('branch_id', openapi.IN_QUERY, description="Идентификатор филиала", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('only_providers', openapi.IN_QUERY, description="Только из списка провайдеров", type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('providers', openapi.IN_QUERY,
                  description="Список провайдеров",
                  type=openapi.TYPE_ARRAY,
                  items=openapi.Items(
                      type=openapi.TYPE_OBJECT,
                      properties={
                          'provider': openapi.Schema(type=openapi.TYPE_STRING, title="Название провайдера", enum=PROVIDER_CHOICES),
                          'count': openapi.Schema(type=openapi.TYPE_INTEGER, title="Количество записей"),
                          'filters': openapi.Schema(type=openapi.TYPE_STRING, title="Фильтры"),
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

    only_providers = request.query_params.get('only_providers')
    if only_providers:
        only_providers = only_providers.lower() == 'true'
    else:
        only_providers = False

    reviews_data = []
    if providers:
        providers = json.loads(providers)
        for prov in providers:
            predata = Review.objects.filter(branch=branch, provider=prov["provider"]).order_by('published_date')
            if "filters" in prov and prov["filters"]:
                predata = predata.filter(parse_filter_string(prov["filters"]))
            if prov["count"]:
                reviews_data += ReviewSerializer(predata[:prov["count"]], many=True).data
            else:
                reviews_data += ReviewSerializer(predata, many=True).data

        if not only_providers:
            provider_to_exclude = [item['provider'] for item in providers]
            reviews_data += ReviewSerializer(Review.objects.filter(branch=branch).exclude(provider__in=provider_to_exclude), many=True).data
 
            
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
            openapi.Parameter('only_providers', openapi.IN_QUERY, description="Только из списка провайдеров", type=openapi.TYPE_BOOLEAN, required=False),
            openapi.Parameter('providers', openapi.IN_QUERY,
                    description="Список провайдеров",
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'provider': openapi.Schema(type=openapi.TYPE_STRING, title="Название провайдера", enum=PROVIDER_CHOICES),
                            'count': openapi.Schema(type=openapi.TYPE_INTEGER, title="Количество записей"),
                            'filters': openapi.Schema(type=openapi.TYPE_STRING, title="Фильтры"),
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
                        ],
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

    only_providers = request.query_params.get('only_providers')
    if only_providers:
        only_providers = only_providers.lower() == 'true'
    else:
        only_providers = False

    providers = request.query_params.get('providers')
    if providers:
        providers = "[" + providers + "]"

    reviews_data = []
    if providers:
        providers = json.loads(providers)
        for prov in providers:
            predata = Review.objects.filter(branch__in=branches, provider=prov["provider"]).order_by('published_date')
            if "filters" in prov and prov["filters"]:
                predata = predata.filter(parse_filter_string(prov["filters"]))
            if prov["count"]:
                reviews_data += ReviewSerializer(predata[:prov["count"]], many=True).data
            else:
                reviews_data += ReviewSerializer(predata, many=True).data
        
        if not only_providers:
            provider_to_exclude = [item['provider'] for item in providers]
            reviews_data += ReviewSerializer(Review.objects.filter(branch__in=branches).exclude(provider__in=provider_to_exclude), many=True).data
 
            
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



@swagger_auto_schema(
    method="GET",
        manual_parameters=[
            ],
        responses={200: '''
                        "ip",
                        "playlists": [{
                            "id",
                            "title",
                            "count",
                            "url",
                            "parse_date",
                            "provider",
                        }],
                        'provider_reviews_count': [
                            {
                                "provider",
                                "review_count"
                            }
                        ],
                        "videos": [
                            {
                                "id",
                                "url",
                                "title",
                                "author",
                                "date",
                                "preview",
                                "duration",
                                "playlist",
                            },
                        ]
                                ''', 400: "Некорректные данные"}
)
@api_view(['GET'])
def get_videos_by_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    objects_with_ip = PlaylistIPMapping.objects.filter(ip_address=ip)
    playlists = []
    for mapping in objects_with_ip:
        playlists.append(mapping.playlist)

    videos_data = []

    videos = Video.objects.filter(playlist__in=playlists)
    videos_serializer = VideoSerializer(videos, many=True)
    videos_data = videos_serializer.data

    playlist_serializer = PlaylistSerializer(playlists, many=True)

    data = {
            'ip': ip,
            'playlists': playlist_serializer.data,
            'provider_viedos_count' : Video.objects.filter(playlist__in=playlists).values('playlist__provider').annotate(review_count=Count('id')),
            'videos': videos_data,
            }
    
    return Response(data)

def parse_filter_string(filter_str):
    """
    Парсит строку фильтра в Q-объекты для Django ORM.
    Поддерживает:
    - равенство: field=value → Q(field=value)
    - не равно: field!=value → ~Q(field=value)
    - другие операторы: field__operator=value → Q(field__operator=value)
    - отрицание операторов: !field__operator=value → ~Q(field__operator=value)
    """
    conditions = Q()
    
    if not filter_str:
        return conditions
    
    for part in filter_str.split('&'):
        if not part:
            continue
        
        if '!=' in part:
            key, value = part.split('!=', 1)
            q_object = ~Q(**{key: value})
        elif '=' in part:
            key, value = part.split('=', 1)
            negate = False
            
            if key.startswith('!'):
                negate = True
                key = key[1:]
            
            if key.endswith('__in'):
                value_list = [v.strip() for v in value.split(',') if v.strip()]
                q_object = Q(**{key: value_list})

            elif key.endswith('__isnull'):
                q_object = Q(**{key: value.lower() == 'true'})
            else:
                q_object = Q(**{key: value})
            if negate:
                q_object = ~q_object
        else:
            continue 
            
        conditions &= q_object
    
    return conditions



from django.http import HttpResponse

def webhook(request):
    print("Request body:", request.body.decode('utf-8'))  # вывод содержимого тела запроса
    return HttpResponse(status=200)