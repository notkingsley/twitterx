release: python manage.py migrate
web: gunicorn --worker-class gthread --threads 4 host.wsgi --log-file -