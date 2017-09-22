from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^/', views.get_price, name='get_price'),
]
