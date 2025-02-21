from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login, name='login'),
    path('callback/', views.callback, name='callback'),
    path('api/top_artists/', views.get_top_artists, name='top_artists'),
    path('api/songs/', views.get_top_songs, name='top_songs'),
    path('api/create_user/', views.create_user, name='create_user'),
    path('api/users/', views.see_users, name='see_users'),
    path('api/users/<str:user>/', views.see_user, name='see_user'),
    path('api/modify_preferences/<str:user>/', views.modify_preferences, name='modify_preferences'),
    path('api/user_delete/<str:user>/', views.delete_user, name='delete_user'),
]
