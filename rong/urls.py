from django.urls import path
from .views import core

app_name = 'rong'
urlpatterns = [
    path('preferences', core.preferences, name='preferences'),
    path('auth/logout', core.logout, name='logout'),
    path('auth/login/discord', core.discordlogin, name='discordlogin'),
    path('auth/login/discord/callback', core.discordcallback, name='discordcallback'),
    path('', core.index, name='index'),
]
