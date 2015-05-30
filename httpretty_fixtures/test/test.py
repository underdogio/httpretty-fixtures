# Load in our dependencies
from unittest import TestCase

import requests

import httpretty_fixtures


# Set up multiple fixture managers
class FakeServer(httpretty_fixtures.FixtureManager):
    @httpretty_fixtures.get('http://localhost:9000/')
    def hello(self, request, uri, res_headers):
        return (200, res_headers, 'world')


class TestHttprettyFixtures(TestCase):
    @FakeServer.run(['hello'])
    def test_request(self):
        """
        A request to a non-existant server behind a running FixtureManager
            receives a response from FixtureManager
        """
        # Make our request
        res = requests.get('http://localhost:9000/')
        self.assertEqual(res.status_code, 200)

        # Assert the content is as expected
        self.assertEqual(res.text, 'world')

        # Assert we have information in our requests
        # self.assertEqual(
