from functools import wraps
import urllib.parse

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import reverse, redirect


def user_passes_test(test_func, login_url=None, redirect_field_name='next'):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            return redirect((login_url if login_url else reverse('rong:discordlogin')) + '?' + urllib.parse.urlencode({redirect_field_name: path}))
        return _wrapped_view
    return decorator


def login_required(function=None, redirect_field_name='next', login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator