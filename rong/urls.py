from django.urls import path

from . import views

app_name = 'rong'
urlpatterns = [
    path('preferences', views.preferences, name='preferences'),
    path('auth/logout', views.logout, name='logout'),
    path('auth/login/discord', views.discordlogin, name='discordlogin'),
    path('auth/login/discord/callback', views.discordcallback, name='discordcallback'),
    path('', views.index, name='index'),
]
