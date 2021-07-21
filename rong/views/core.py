from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from requests.exceptions import HTTPError

from rong.decorators import login_required
from rong.discord import make_session
from rong.forms.preferences import PreferencesForm
from rong.models import User, Unit


# Create your views here.

@login_required
def preferences(request: HttpRequest):
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Preferences saved.')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid preferences.')
    else:
        form = PreferencesForm(instance=request.user)
    return render(request, 'rong/preferences.html', {'form': form})


@login_required
def logout(request: HttpRequest):
    del request.session['user_id']
    return redirect(reverse('rong:index'))


def discordcallback(request: HttpRequest):
    if request.method == 'GET':
        if request.GET.get('error'):
            return HttpResponse('HeyGuys %s' % request.GET['error'])
        try:
            discord = make_session(request, state=request.session.get('oauth2_state'))
            token = discord.fetch_token(
                settings.DISCORD_TOKEN_URL,
                client_secret=settings.DISCORD_CLIENT_SECRET,
                authorization_response=request.build_absolute_uri())
            user = User.for_discord_session(discord)
            user.check_single_mode()
            destination = request.session.get('redirect_url', '')
            if not destination:
                destination = reverse('rong:index')
            if 'redirect_url' in request.session:
                del request.session['redirect_url']
            del request.session['oauth2_state']
            request.session['user_id'] = user.id
            request.session.set_expiry(64800)
            return redirect(destination)
        except HTTPError:
            raise PermissionDenied
    else:
        raise PermissionDenied


def discordlogin(request: HttpRequest):
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


def index(request: HttpRequest):
    return render(request, 'rong/index.html', {})


def unitselect(request: HttpRequest):
    ctx = {
        "units": Unit.valid_units()
    }
    return render(request, 'rong/test_unitselect.html', ctx)
