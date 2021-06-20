from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from .models import User, AnonymousUser


def get_user(request):
    if not hasattr(request, '_cached_user'):
        # do stuff
        request._cached_user = AnonymousUser()
        if request.session.get('user_id', None):
            request._cached_user = User.objects.filter(pk=request.session['user_id']).first() or AnonymousUser()

    return request._cached_user


class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Rong authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'rong.middleware.AuthenticationMiddleware'."
        )
        request.user = SimpleLazyObject(lambda: get_user(request))
