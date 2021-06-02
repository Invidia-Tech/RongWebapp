from rong.models import Clan, ClanBattle
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpRequest
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from rong.discord import make_session
from rong.models import User
from django.db import connection
from django.utils.http import url_has_allowed_host_and_scheme
from rong.decorators import login_required
from requests.exceptions import HTTPError
from django.contrib import messages
from rong.forms import PreferencesForm

# Create your views here.

def view_battle(request, battle):
    clan_battle = get_object_or_404(ClanBattle, slug=battle)
    if not request.user.can_view(clan_battle):
        raise SuspiciousOperation()
    # do something
    return HttpResponse('Pasta')

@login_required
def list_battles(request, clan):
    clan = get_object_or_404(Clan, slug=clan)
    if not request.user.can_view(clan):
        raise SuspiciousOperation()
    # do something
    return render(request, 'rong/clanbattle/list.html', {"clan": clan})
