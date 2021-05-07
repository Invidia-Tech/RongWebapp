# below from https://github.com/andrefarzat/django-webp/blob/master/django_webp/context_processors.py
from django.conf import settings
import httpagentparser

WEBP_VALID_BROWSERS = getattr(settings, 'WEBP_VALID_BROWSERS', ['Chrome', 'Opera', 'Opera Mobile'])


def _check_by_user_agent(user_agent):
    """ Checks if the client accepts checking the given user_agent """
    if user_agent:
        data = httpagentparser.detect(user_agent)
        if 'browser' in data:
            return data['browser']['name'] in WEBP_VALID_BROWSERS

    return False


def _check_by_http_accept_header(http_accept):
    return 'webp' in http_accept


def supports_webp(request):
    """ Adds `supports_webp` value in the context """
    user_agent = request.META.get('HTTP_USER_AGENT')
    http_accept = request.META.get('HTTP_ACCEPT', '')

    if _check_by_http_accept_header(http_accept):
        supports_webp = True
    elif _check_by_user_agent(user_agent):
        supports_webp = True
    else:
        supports_webp = False
    
    return supports_webp
