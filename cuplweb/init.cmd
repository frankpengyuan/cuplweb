# install mysql
# add mysql to PATH

pip install django
pip install mysqlclient

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser