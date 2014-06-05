"""
Middleware for identify the location of visitor.

Middleware adds `country_code` in session.

Usage:

# To enable the Geoinfo feature on a per-view basis, use:
decorator `django.utils.decorators.decorator_from_middleware(middleware_class)`

"""

import logging
import pygeoip

from ipware.ip import get_ip
from django.conf import settings

log = logging.getLogger(__name__)


class CountryMiddleware(object):
    """
    Middleware for obtain country info.

    """
    def process_response(self, request, response):
        """
        Process detection.
        """
        if request.user.is_authenticated():
            ip = get_ip(request)
            country_code = pygeoip.GeoIP(settings.GEOIP_PATH).country_code_by_addr(ip)
            request.session['country_code'] = country_code
            log.debug('Country code is set to %s', country_code)
        return response


