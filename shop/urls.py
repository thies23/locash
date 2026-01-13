from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/<str:username>/', views.user_detail, name='user_detail_username'),
    path('user/id/<str:id12>/', views.user_detail, name='user_detail'),
    path('manage/', views.manage, name='manage'),
]
