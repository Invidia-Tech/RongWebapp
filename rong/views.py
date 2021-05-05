from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from .discord import make_session
import urllib.parse

# Create your views here.
def discordcallback(request : HttpRequest):
    if request.method == 'GET':
        if request.GET.get('error'):
            return HttpResponse('HeyGuys %s' % request.GET['error'])
        discord = make_session(request, state=request.session.get('oauth2_state'))
        token = discord.fetch_token(
            settings.DISCORD_TOKEN_URL,
            client_secret=settings.DISCORD_CLIENT_SECRET,
            authorization_response=request.build_absolute_uri())
        request.session['discord_token'] = token
        return HttpResponse('HeyGuys')
    else:
        raise PermissionDenied

def discordlogin(request : HttpRequest):
    discord = make_session(request, scope=['identify', 'guilds'])
    authorization_url, state = discord.authorization_url(settings.DISCORD_OAUTH_URL)
    request.session['oauth2_state'] = state
    request.session.set_expiry(3600)
    return redirect(authorization_url)

def index(request : HttpRequest):
    return render(request, 'rong/index.html', {})
