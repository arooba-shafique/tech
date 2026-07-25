from datetime import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings


class TrialExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Skip for superusers
        if request.user.is_superuser:
            return self.get_response(request)

        # Skip for exempted paths
        path = request.path
        exempt_prefixes = [
            '/admin/',
            '/trial-expired/',
            '/static/',
            '/media/',
        ]
        if any(path.startswith(p) for p in exempt_prefixes):
            return self.get_response(request)

        # Check trial expiry
        user = request.user
        school = getattr(user, 'school', None)
        if school and school.trial_end_date:
            if timezone.now() > school.trial_end_date:
                return HttpResponse(
                    render_to_string('trial_expired.html', {'school': school}),
                    status=403
                )

        return self.get_response(request)
