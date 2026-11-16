from django.urls import path

from . import views

urlpatterns = [
    path('', views.circle_detail, name='circle_detail'),
    path('create/', views.circle_create, name='circle_create'),
    path('edit/', views.circle_edit, name='circle_edit'),
    path('delete/', views.circle_delete, name='circle_delete'),
    path('join/', views.circle_join, name='circle_join'),
    path('leave/', views.leave_circle, name='leave_circle'),
    path('members/<int:member_id>/remove/', views.remove_member, name='remove_member'),
]