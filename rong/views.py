from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from .discord import make_session
from .models import User
from django.db import connection
from django.utils.http import url_has_allowed_host_and_scheme
from .decorators import login_required

# Create your views here.

@login_required
def privileged(request : HttpRequest):
    return HttpResponse("You privileged person, you.")

@login_required
def logout(request: HttpRequest):
    del request.session['user_id']
    return redirect(reverse('rong:index'))

def discordcallback(request : HttpRequest):
    if request.method == 'GET':
        if request.GET.get('error'):
            return HttpResponse('HeyGuys %s' % request.GET['error'])
        discord = make_session(request, state=request.session.get('oauth2_state'))
        token = discord.fetch_token(
            settings.DISCORD_TOKEN_URL,
            client_secret=settings.DISCORD_CLIENT_SECRET,
            authorization_response=request.build_absolute_uri())
        user = User.for_discord_session(discord)
        destination = request.session.get('redirect_url', '')
        if not destination:
            destination = reverse('rong:index')
        if 'redirect_url' in request.session:
            del request.session['redirect_url']
        del request.session['oauth2_state']
        request.session['user_id'] = user.id
        request.session.set_expiry(64800)
        return redirect(destination)
    else:
        raise PermissionDenied

def discordlogin(request : HttpRequest):
    discord = make_session(request, scope=['identify', 'guilds'])
    authorization_url, state = discord.authorization_url(settings.DISCORD_OAUTH_URL)
    request.session['oauth2_state'] = state
    request.session['redirect_url'] = ''
    if 'next' in request.GET:
        safe = url_has_allowed_host_and_scheme(
            url=request.GET['next'],
            allowed_hosts=request.get_host(),
            require_https=request.is_secure()
        )
        if safe:
            request.session['redirect_url'] = request.GET['next']
    
    request.session.set_expiry(3600)
    return redirect(authorization_url)

def index(request : HttpRequest):
    return render(request, 'rong/index.html', {})
