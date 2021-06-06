from django.urls import path
from .views import core, box, clanbattle, manageclan

app_name = 'rong'
urlpatterns = [
    path('clan/<slug:clan>/members', manageclan.list_members, name='clan_list_members'),
    path('clanbattle/list/<slug:clan>/', clanbattle.list_battles, name='cb_list'),
    path('clanbattle/<slug:battle>/', clanbattle.view_battle, name='cb_view'),
    path('box/', box.index, name='box_index'),
    path('box/create/', box.create_box, name='box_create'),
    path('box/<int:box_id>/', box.alter_box, name='box_alter'),
    path('box/<int:box_id>/unit/create/', box.create_boxunit, name='box_createunit'),
    path('box/<int:box_id>/unit/<int:boxunit_id>/', box.alter_boxunit, name='box_alterunit'),
    path('preferences/', core.preferences, name='preferences'),
    path('auth/logout/', core.logout, name='logout'),
    path('auth/login/discord/', core.discordlogin, name='discordlogin'),
    path('auth/login/discord/callback/', core.discordcallback, name='discordcallback'),
    path('unitselect/', core.unitselect, name='unitselect'),
    path('', core.index, name='index'),
]
