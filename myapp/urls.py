from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /polls/
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    url(r'^abcd/$', views.detail, name='detail'),
    # ex: /polls/5/results/
    url(r'^late/$', views.results, name='results'),
    # ex: /polls/5/vote/
    url(r'^billing/$', views.vote, name='vote'),
]