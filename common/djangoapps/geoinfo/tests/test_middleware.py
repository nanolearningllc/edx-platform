"""
Tests for CountryMiddleware
"""

from mock import Mock, patch
import pygeoip
import unittest

from django.conf import settings
from django.test import TestCase, Client
from django.test.utils import override_settings
from django.test.client import RequestFactory
from courseware.tests.tests import TEST_DATA_MONGO_MODULESTORE
from student.models import CourseEnrollment
from student.tests.factories import UserFactory, AnonymousUserFactory
from xmodule.modulestore.tests.factories import CourseFactory

from django.contrib.sessions.middleware import SessionMiddleware
from geoinfo.middleware import CountryMiddleware

@override_settings(MODULESTORE=TEST_DATA_MONGO_MODULESTORE)
class CountryMiddlewareTests(TestCase):
    """
    Tests of CountryMiddleware.
    """
    def setUp(self):
        self.country_middleware = CountryMiddleware()
        self.session_middleware = SessionMiddleware()
        self.authenticated_user = UserFactory.create()
        self.anonymous_user = AnonymousUserFactory.create()
        self.request_factory = RequestFactory()
        self.response = Mock()
        self.patcher = patch.object(pygeoip.GeoIP, 'country_code_by_addr', self.mock_country_code_by_addr)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def mock_country_code_by_addr(self, ip_addr):
        """
        Gives us a fake set of IPs
        """
        ip_dict = {
            '1.0.0.0': 'CU',
        }
        return ip_dict.get(ip_addr, 'US')

    def test_country_code_added(self):
        request = self.request_factory.get('/somewhere', 
                                            HTTP_X_FORWARDED_FOR='1.0.0.0',
                                            REMOTE_ADDR='1.0.0.0'
                                        )
        request.user = self.authenticated_user
        self.session_middleware.process_request(request)
        # No country code exists before request.
        self.assertNotIn('country_code', request.session)
        self.country_middleware.process_response(request, self.response)
        # Country code added to session.
        self.assertEqual('CU', request.session.get('country_code'))

    def test_user_not_authenticated(self):
        request = self.request_factory.get('/somewhere', 
                                            HTTP_X_FORWARDED_FOR='1.0.0.0',
                                            REMOTE_ADDR='1.0.0.0'
                                        )
        request.user = self.anonymous_user
        self.session_middleware.process_request(request)
        # No country code exists before request.
        self.assertNotIn('country_code', request.session)
        self.country_middleware.process_response(request, self.response)
        # Country code is not set for anonymous user.
        self.assertNotIn('country_code', request.session)


