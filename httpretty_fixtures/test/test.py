# Load in our dependencies
from unittest import TestCase

import requests

import httpretty_fixtures


# Set up multiple fixture managers
class FakeServer(httpretty_fixtures.FixtureManager):
    @httpretty_fixtures.get('http://localhost:9000/')
    def hello(self, request, uri, res_headers):
        return (200, res_headers, 'world')


class CounterServer(httpretty_fixtures.FixtureManager):
    def __init__(self):
        self.count = 0
        super(CounterServer, self).__init__()

    @httpretty_fixtures.get('http://localhost:9000/')
    def counter(self, request, uri, res_headers):
        self.count += 1
        return (200, res_headers, str(self.count))


# Define our tests
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
    def test_multiple_requests(self):
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

    @CounterServer.run(['count'])
    def test_state_preserved(self):
        """
        Multiple stateful requests to a running FixtureManager
            receive appropriate state
        """
        # Make our first request and verify its count
        res = requests.get('http://localhost:9000/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, '1')

        # Make our second request and verify its count
        res = requests.get('http://localhost:9000/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, '2')

    @CounterServer.run(['count'])
    def test_state_disjoint(self):
        """
        A separately running FixtureManager
            does not receive state from past runs
        """
        # Verifies that we don't get bleed from `test_state_preserved`
        res = requests.get('http://localhost:9000/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, '1')
