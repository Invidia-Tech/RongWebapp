from django.http import HttpRequest
from .models import AnonymousUser
from .helpers.webp import supports_webp

def auth(request : HttpRequest):
    if hasattr(request, 'user'):
        user = request.user
    else:
        user = AnonymousUser()
    
    return {
        'user': user
    }

def webp(request : HttpRequest):
    return {'supports_webp': supports_webp(request)}
