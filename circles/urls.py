from django.urls import path

from . import views

urlpatterns = [
    path('', views.circle_detail, name='circle_detail'),
    path('create/', views.circle_create, name='circle_create'),
]