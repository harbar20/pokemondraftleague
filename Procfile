web: gunicorn pokemondraftleague.wsgi
worker: celery worker -A pokemondraftleague -l info
processor: celery -A pokemondraftleague worker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
worker2: python discordbot/discordbot.py