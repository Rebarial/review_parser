from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from common_parser.tools.parse import parse_all_providers, create_yandex_reviews, create_2gis_reviews, create_google_reviews, create_vlru_reviews
from common_parser.tools.parse_videos import parse_youtube_videos
from common_parser.models import Branch, Playlist
from django.shortcuts import get_object_or_404
from loguru import logger

logger.add("debug.log", enqueue=True, format="{time} {level} {message}", level="DEBUG")


@shared_task(name='common_parser.tasks.weekly_parsing')
def weekly_parsing():
    branches = Branch.objects.all()

    dict_results = {}
    for branch in branches:
        dict_results[f"{branch.id}"] = parse_all_providers(branch)

    return dict_results


@shared_task(name='parse_all_providers_async_on_create')
def parse_all_providers_async_on_create(branch_org_id, branch_address):
    try:
        branch = Branch.objects.get(
            organization_id=branch_org_id,
            address=branch_address
        )
        return parse_all_providers(branch)
    except Branch.DoesNotExist:
        logger.error(f"Branch not found (org_id={branch_org_id}, address={branch_address})")
    except Exception as e:
        logger.error(f"Error in parse_all_providers_async_on_create: {e}")

@shared_task(name='parse_all_providers_async')
def parse_all_providers_async(branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    return {'branch_id': branch_id,
            'results': parse_all_providers(branch)
            }

@shared_task(name='parse_yandex_async')
def parse_yandex_async(branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    return {'branch_id': branch_id,
            'results': create_yandex_reviews(url=branch.yandex_map_url, inn=branch.organization.inn, address=branch.address)
            }

@shared_task(name='parse_google_async')
def parse_google_async(branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    return {'branch_id': branch_id,
            'results': create_google_reviews(url=branch.google_map_url, inn=branch.organization.inn, address=branch.address)
            }

@shared_task(name='parse_vlru_async')
def parse_vlru_async(branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    return {'branch_id': branch_id,
            'results': create_vlru_reviews(branch.vlru_url, branch.organization.inn, address=branch.address),
            }

@shared_task(name='parse_2gis_async')
def parse_2gis_async(branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    return {'branch_id': branch_id,
            'results': create_2gis_reviews(url=branch.twogis_map_url, inn=branch.organization.inn, address=branch.address)
            }


@shared_task(name='parse_youtube_videos_async')
def parse_youtube_videos_async(playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    return {'playlist_id': playlist_id,
            'results': parse_youtube_videos(playlist.url)
            }
