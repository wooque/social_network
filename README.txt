Install:

Create and activate virtualenv:
virtualenv virtualenv
source virtualenv/bin/activate

Install packages:
pip install -r requirements.txt

Migrate:
python manage.py migrate

Running social_network requires PostgreSQL and Redis running:
sudo sytemctl start postgresql redis-server

Run Celery:
celery -A social_network worker -l info

Run Django REST server:
python manage.py runserver
