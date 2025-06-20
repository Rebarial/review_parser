import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv



load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'review_parser.settings')

app = Celery('review_parser')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.result_backend = 'django-db'
app.conf.broker_connection_retry_on_startup = True
app.conf.broker_connection_retry = True
app.conf.broker_connection_max_retries = 1

# Настройка периодических задач
app.conf.beat_schedule = {
    'weekly-sunday-6am-task': {
        'task': 'common_parser.tasks.weekly_parsing',
        'schedule': crontab(hour=6, minute=0, day_of_week='sun'),
    },
}


app.autodiscover_tasks()