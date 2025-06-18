from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from common_parser.tools.parse import parse_all_providers
from common_parser.models import Branch

@shared_task(name='common_parser.tasks.weekly_parsing')
def weekly_parsing():
    branches = Branch.objects.all()

    for branch in branches:
        parse_all_providers(branch)