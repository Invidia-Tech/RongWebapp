from django.http import HttpRequest

from .models import AnonymousUser


def auth(request: HttpRequest):
    if hasattr(request, 'user'):
        user = request.user
    else:
        user = AnonymousUser()

    return {
        'user': user
    }
