# Load in our dependencies
from unittest import TestCase

import requests

from httpretty_fixtures import FixtureManager


# Set up multiple fixture managers
class FakeServer(FixtureManager):
    @FixtureManager.get('http://localhost:9000/')
    def hello(self, request, uri, res_headers):
        return (200, res_headers, 'world')


class TestHttprettyFixtures(TestCase):
    @FakeServer.run(['hello'])
    def test_request(self):
        """
        A request to a non-existant server behind a running FixtureManager
            receives a response from FixtureManager
        """
        res = requests.get('http://localhost:9000/')
        print res.status_code
