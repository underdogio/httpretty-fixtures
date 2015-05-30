# Load in our dependencies
from unittest import TestCase

import requests

import httpretty_fixtures


# Set up multiple fixture managers
FakeServer = httpretty_fixtures.FixtureManager()


@FakeServer.get('http://localhost:9000/')
def hello(request, uri, res_headers):
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
