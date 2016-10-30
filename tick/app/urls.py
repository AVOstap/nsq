# coding: utf-8

from django.conf.urls import url, include
from app import views


base_patterns = [
    url(r'^(?P<tick>\w+)/analytics$', views.analytics, name='analytics'),
    url(r'^(?P<tick>\w+)/delta$', views.delta, name='delta'),
    url(r'^(?P<tick>\w+)/insider/(?P<name>.+)$', views.insider_trade, name='insider_trade'),
    url(r'^(?P<tick>\w+)/insider$', views.insider, name='insider'),
    url(r'^(?P<tick>\w+)$', views.ticker, name='ticker'),
    url(r'^$', views.index, name='index'),
]

urlpatterns = [
    url(r'^api/', include(base_patterns), {'is_json_response': True}),
    url(r'', include(base_patterns), {'is_json_response': False}),
]
