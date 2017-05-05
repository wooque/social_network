Install:

Create and activate virtualenv:
virtualenv virtualenv
source virtualenv/bin/activate

Install packages:
pip install -r requirements.txt

Running social_network requires PostgreSQL and Redis running:
sudo systemctl start postgresql redis

Create DB and DB user:
sudo -u postgres ./create_db.sh mys3cretepswd

Migrate:
python manage.py migrate

Optionally load data:
python manage.py loaddata auth_user
python manage.py loaddata wall

Run Celery:
celery -A social_network worker -l info

Run Django REST server:
python manage.py runserver
