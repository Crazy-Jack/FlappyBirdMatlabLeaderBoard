from django.urls import re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    # Render pages
    re_path(r'^$', views.render_search_page, name='tools'),
    re_path(r'^user/$', views.render_login_page, name='profile'),
    re_path(r'^register/$', views.create_user, name='register'),
    re_path(r'^login/$', views.loguserin, name='login'),
    re_path(r'^logout/$', views.loguserout, name='logout'),

    re_path(r'^c1/$', views.render_c1_page, name='category1'),
    re_path(r'^c2/$', views.render_c2_page, name='category2'),
    re_path(r'^c3/$', views.render_c3_page, name='category3'),
    re_path(r'^upload/$', views.render_upload_page, name='upload'),
    # url(r'^stats/$', views.render_stats_page, name='tools_stats'),

    # # Upload
    re_path(r'^submit/$', views.save_to_files, name='submit'),

    # get user table
    re_path(r'^get_user_data/$', views.get_user_data),
    re_path(r'^delete_md5/$', views.delete_md5),

    # # check statistics
    # url(r'^get_stats/$', views.get_stats, name='get_stats'),

    # # check meta statistics
    # url(r'^get_meta_stats/$', views.get_meta_stats, name='get_meta_stats'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

