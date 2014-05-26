import logging

import pygeoip
from ipware.ip import get_ip

from django.conf import settings

log = logging.getLogger(__name__)

class CountryMiddleware(object):
    """
    Middleware for obtain country info.

    """
    def __init__(self):
        """
        Read settings and decide enable detecting or not.
        """
        if not settings.FEATURES.get('ENABLE_GEOINFO', False):
            raise MiddlewareNotUsed()


    def process_request(self, request):
        """
        Process detection.
        """
        if not request.session.get('country_code', False):
            ip = get_ip(request)
            country_code = pygeoip.GeoIP(settings.GEOIP_PATH).country_code_by_addr(ip)
            request.session['country_code'] = country_code
            log.info('Country code is set to %s', country_code)
        log.info('Country code remains: %s', request.session['country_code'])


