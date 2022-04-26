from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    # Render pages
    url(r'^$', views.render_search_page, name='tools'),
    url(r'^user/$', views.render_login_page, name='profile'),
    url(r'^register/$', views.create_user, name='register'),
    url(r'^login/$', views.loguserin, name='login'),
    url(r'^logout/$', views.loguserout, name='logout'),

    url(r'^c1/$', views.render_c1_page, name='category1'),
    url(r'^c2/$', views.render_c2_page, name='category2'),
    url(r'^c3/$', views.render_c3_page, name='category3'),
    url(r'^upload/$', views.render_upload_page, name='upload'),
    # url(r'^stats/$', views.render_stats_page, name='tools_stats'),

    # # Upload
    url(r'^submit/$', views.save_to_files, name='submit'),

    # get user table
    url(r'^get_user_data/$', views.get_user_data),
    url(r'^delete_md5/$', views.delete_md5),

    # # check statistics
    # url(r'^get_stats/$', views.get_stats, name='get_stats'),

    # # check meta statistics
    # url(r'^get_meta_stats/$', views.get_meta_stats, name='get_meta_stats'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

