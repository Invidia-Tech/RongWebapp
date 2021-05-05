from django.http import HttpRequest
from django.conf import settings
from django.urls import reverse
from requests_oauthlib import OAuth2Session

def token_updater(request : HttpRequest, token):
    request.session['discord_token'] = token

def make_session(request : HttpRequest, token=None, state=None, scope=None):
    redirect_url = request.build_absolute_uri(reverse('rong:discordcallback'))
    return OAuth2Session(
        client_id=settings.DISCORD_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=redirect_url,
        auto_refresh_kwargs={
            'client_id': settings.DISCORD_CLIENT_ID,
            'client_secret': settings.DISCORD_CLIENT_SECRET,
        },
        auto_refresh_url=settings.DISCORD_TOKEN_URL,
        token_updater=lambda tok: token_updater(request, tok))
