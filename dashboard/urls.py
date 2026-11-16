from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('member-dashboard/', views.member_dashboard, name='member_dashboard'),
]