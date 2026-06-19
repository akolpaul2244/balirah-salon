web: gunicorn balirah_salon.wsgi:application --config gunicorn.conf.py
worker: celery -A balirah_salon worker --loglevel=info --concurrency=2
beat: celery -A balirah_salon beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
