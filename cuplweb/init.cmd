# install mysql
# add mysql to PATH

pip install django
pip install mysqlclient
pip install django-ratelimit

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser