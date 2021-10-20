from django.urls import path
from .views import core, box, clanbattle, manageclan, api

app_name = 'rong'
urlpatterns = [
    path('api/add_hit/', api.add_hit, name='api_add_hit'),
    path('clan/<slug:clan>/tags/<int:tag_id>/', manageclan.edit_hit_tag, name='clan_edit_hit_tag'),
    path('clan/<slug:clan>/tags/add/', manageclan.add_hit_tag, name='clan_add_hit_tag'),
    path('clan/<slug:clan>/tags/', manageclan.list_hit_tags, name='clan_list_hit_tags'),
    path('clan/<slug:clan>/battles/<int:battle_id>/editgroup/<int:group_id>/', manageclan.edit_hit_group, name='clan_edit_hit_group'),
    path('clan/<slug:clan>/battles/<int:battle_id>/addgroup/', manageclan.add_hit_group, name='clan_add_hit_group'),
    path('clan/<slug:clan>/battles/<int:battle_id>/', manageclan.edit_battle, name='clan_edit_battle'),
    path('clan/<slug:clan>/battles/add/', manageclan.add_battle, name='clan_add_battle'),
    path('clan/<slug:clan>/battles/', manageclan.list_battles, name='clan_list_battles'),
    path('clan/<slug:clan>/members/<int:member_id>/', manageclan.edit_member, name='clan_edit_member'),
    path('clan/<slug:clan>/members/', manageclan.list_members, name='clan_list_members'),
    path('clanbattle/list/<slug:clan>/', clanbattle.list_battles, name='cb_list'),
    path('clanbattle/<slug:battle>/hits/<int:hit_id>/', clanbattle.edit_hit, name='cb_edit_hit'),
    path('clanbattle/<slug:battle>/hits/add/', clanbattle.add_hit, name='cb_add_hit'),
    path('clanbattle/<slug:battle>/hits/data/', clanbattle.hit_log_data, name='cb_list_hits_data'),
    path('clanbattle/<slug:battle>/hits/', clanbattle.hit_log, name='cb_list_hits'),
    path('clanbattle/<slug:battle>/', clanbattle.view_battle, name='cb_view'),
    path('box/', box.index, name='box_index'),
    path('box/create/', box.create_box, name='box_create'),
    path('box/<int:box_id>/', box.alter_box, name='box_alter'),
    path('box/<int:box_id>/unit/create/', box.create_boxunit, name='box_createunit'),
    path('box/<int:box_id>/unit/<int:boxunit_id>/', box.alter_boxunit, name='box_alterunit'),
    path('box/<int:box_id>/import/', box.import_box, name='box_import'),
    path('preferences/', core.preferences, name='preferences'),
    path('auth/logout/', core.logout, name='logout'),
    path('auth/login/discord/', core.discordlogin, name='discordlogin'),
    path('auth/login/discord/callback/', core.discordcallback, name='discordcallback'),
    path('', core.index, name='index'),
]
