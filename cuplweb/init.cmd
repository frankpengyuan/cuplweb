# install mysql
sudo apt-get install mysql-server mysql-client
# add mysql to PATH

# ubuntu
sudo apt-get install python-dev libmysqlclient-dev
sudo pip install mysql-python
pip install django django-ratelimit django-bulk-update

# windows
pip install django mysqlclient django-ratelimit django-bulk-update

CREATE USER 'cuplweb'@'localhost' IDENTIFIED BY '3wer@#frwf423FRe$T';
GRANT ALL PRIVILEGES ON *.* TO 'cuplweb'@'localhost' WITH GRANT OPTION;
CREATE DATABASE cuplweb CHARACTER SET utf8 COLLATE utf8_general_ci;

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
