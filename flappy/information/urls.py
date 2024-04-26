from django.urls import re_path
from . import views
from django.conf import settings


urlpatterns = [
	re_path(r'^about$', views.about, name = 'about'),
	re_path(r'^manual$', views.manual, name = 'manual'),
	re_path(r'^metadata$', views.meta_data, name = 'metadata'),
]