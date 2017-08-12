from django.contrib.auth import views as auth_views
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^choose_cat/', views.choose_cat, name='choose_cat'),
    url(r'^confirm$', views.confirm, name='confirm'),
    url(r'^finish/', views.finish, name='finish'),
    url(r'^login/', views.mylogin, name='mylogin'),
    url(r'^logout/', views.mylogout, name='logout'),
    url(r'^offline$', views.offline, name='offline'),
    url(r'^special_req/([0-9]*)', views.special_req, name='special_req'),
    url(r'^timetable/([1-5]{1})', views.timetable, name='timetable'),
    url(r'^userinfo/', views.userinfo, name='userinfo'),
]

handler404 = views.error_handler
