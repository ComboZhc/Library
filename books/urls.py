from django.conf.urls.defaults import patterns, url
from views import index, new, edit
urlpatterns = patterns('',
    url(r'^$', index),
    url(r'^new/$', new),
    url(r'^edit/(\d+)/$', edit),
)