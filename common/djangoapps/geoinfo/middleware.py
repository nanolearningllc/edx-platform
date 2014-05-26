import pygeoip
from ipware.ip import get_ip

from django.conf import settings

class CountryMiddleware(object):
    """
    Middleware for obtain country info.

    """
    def __init__(self):
        """
        Read settings and decide enable detecting or not.
        """
        pass


    def process_request(self, request):
        """
        Process detection.
        """
        if not request.session.get('country_code', False):
            ip = get_ip(request)
            country_code = pygeoip.GeoIP(settings.GEOIP_PATH).country_code_by_addr(ip)
            request.session['country_code'] = country_code


