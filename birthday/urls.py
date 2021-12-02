from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('media/', views.media, name='media'),
    path('media/<int:page>/', views.media_list, name='media_list'),
    path('updates/<int:page>/', views.updates, name='updates'),
    path('search/', views.search, name='search'),
    path('test/', views.test, name='test'),
]
