from django.urls import re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    re_path(r'^$', views.render_home)
]
