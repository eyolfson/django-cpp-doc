from django.conf.urls import url

from . import views

app_name = 'cpp_doc'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^package/$', views.PackageNameIndexView.as_view(), name='package_name_list'),
    url(r'^package/(?P<slug>[A-Za-z][-.\w]*)/$', views.PackageIndexView.as_view(),
        name='package_list'),
    url(r'^package/(?P<slug>[A-Za-z][-.\w]*)/(?P<version>[-\w\.]+)/$',
        views.PackageDetailView.as_view(),
        name='package_detail'),

    url(r'^package/(?P<slug>[A-Za-z][-.\w]*)/(?P<version>[-\w\.]+)/file/$',
        views.file_root,
        name='file_root'),
    url(r'^package/(?P<slug>[A-Za-z][-.\w]*)/(?P<version>[i\w\.]+)/file/(?P<fd_pk>[0-9]+)/$',
        views.file_detail,
        name='file_detail'),

    url(r'^package/(?P<slug>[A-Za-z][-.\w]*)/(?P<version>[-\w\.]+)/decl/$',
        views.decl_root,
        name='decl_root'),
    url(r'^package/(?P<slug>[A-Za-z][-.\w]*)/(?P<version>[-\w\.]+)/decl/(?P<decl_pk>[0-9]+)/$',
        views.decl_detail,
        name='decl_detail'),
]
