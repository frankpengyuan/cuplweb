# install mysql
# add mysql to PATH

pip install django, mysqlclient, django-ratelimit

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser