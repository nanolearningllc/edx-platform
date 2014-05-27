"""
Middleware for identify the location of visitor.

Middleware adds `country_code` in session.

Usage:

# Enable the middleware in your settings

# To enable the Geoinfo feature for the whole site, set:
FEATURES['ENABLE_GEOINFO'] = True

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

    def process_request(self, request):
        """
        Process detection.
        """
        if not request.session.get('country_code', False):
            ip = get_ip(request)
            country_code = pygeoip.GeoIP(settings.GEOIP_PATH).country_code_by_addr(ip)
            request.session['country_code'] = country_code
            log.debug('Country code is set to %s', country_code)
        log.debug('Country code remains: %s', request.session['country_code'])


