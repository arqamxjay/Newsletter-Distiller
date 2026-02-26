web: gunicorn wsgi:app
worker: celery -A app.workers.tasks worker --loglevel=info
beat: celery -A app.workers.tasks beat --loglevel=info
