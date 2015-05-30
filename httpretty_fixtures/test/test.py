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
        self.assertEqual(httpretty_fixtures.first_request().path, '/')
        self.assertEqual(httpretty_fixtures.last_request().path, '/')
        self.assertEqual(len(httpretty_fixtures.requests()), 1)
        self.assertEqual(httpretty_fixtures.requests()[0].path, '/')

    @FakeServer.run(['hello'])
    def test_multiple_request(self):
        """
        Multiple requests to a running FixtureManager
            separates requests
        """
        # Make our request
        res = requests.get('http://localhost:9000/?first')
        self.assertEqual(res.status_code, 200)
        res = requests.get('http://localhost:9000/?second')
        self.assertEqual(res.status_code, 200)

        # Assert we have information in our requests
        self.assertEqual(httpretty_fixtures.first_request().path, '/?first')
        self.assertEqual(httpretty_fixtures.last_request().path, '/?second')
        self.assertEqual(len(httpretty_fixtures.requests()), 2)
        self.assertEqual(httpretty_fixtures.requests()[0].path, '/?first')
        self.assertEqual(httpretty_fixtures.requests()[1].path, '/?second')
