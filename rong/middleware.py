from django.utils.deprecation import MiddlewareMixin
from .discord import make_session
from django.utils.functional import SimpleLazyObject

def get_user(request):
    if not hasattr(request, '_cached_user'):
        # do stuff
    return request._cached_user

class AuthenticationMiddleware(MiddlewareMixin):
    

