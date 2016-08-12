# Load in our dependencies
from unittest import TestCase

import httpretty
import requests

import httpretty_fixtures


# Set up multiple fixture managers
class FakeServer(httpretty_fixtures.FixtureManager):
    @httpretty_fixtures.get('http://localhost:9000/')
    def hello(self, request, uri, res_headers):
        return (200, res_headers, 'world')

    @httpretty_fixtures.get('http://localhost:9000/goodbye')
    def goodbye(self, request, uri, res_headers):
        return (200, res_headers, 'moon')


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
    def test_request(self, fake_server):
        """
        A request to a non-existant server behind a running FixtureManager
            receives a response from FixtureManager
            collects the request for later access
        """
        # Make our request
        res = requests.get('http://localhost:9000/')
        self.assertEqual(res.status_code, 200)

        # Assert the content is as expected
        self.assertEqual(res.text, 'world')

        # Assert we have information in our requests from `httpretty` context
        self.assertEqual(httpretty_fixtures.first_request().path, '/')
        self.assertEqual(httpretty_fixtures.last_request().path, '/')
        self.assertEqual(len(httpretty_fixtures.requests()), 1)
        self.assertEqual(httpretty_fixtures.requests()[0].path, '/')

        # Assert we have information in our requests from fixture context
        fixture = fake_server.hello
        self.assertEqual(fixture.first_request.path, '/')
        self.assertEqual(fixture.last_request.path, '/')
        self.assertEqual(len(fixture.requests), 1)
        self.assertEqual(fixture.requests[0].path, '/')

    @FakeServer.run(['hello'])
    def test_multiple_requests(self, fake_server):
        """
        Multiple requests to a running FixtureManager
            collects separate requests
        """
        # Make our request
        res = requests.get('http://localhost:9000/?first')
        self.assertEqual(res.status_code, 200)
        res = requests.get('http://localhost:9000/?second')
        self.assertEqual(res.status_code, 200)

        # Assert we have information in our requests from `httpretty` context
        self.assertEqual(httpretty_fixtures.first_request().path, '/?first')
        self.assertEqual(httpretty_fixtures.last_request().path, '/?second')
        self.assertEqual(len(httpretty_fixtures.requests()), 2)
        self.assertEqual(httpretty_fixtures.requests()[0].path, '/?first')
        self.assertEqual(httpretty_fixtures.requests()[1].path, '/?second')

        # Assert we have information in our requests from fixture context
        fixture = fake_server.hello
        self.assertEqual(fixture.first_request.path, '/?first')
        self.assertEqual(fixture.last_request.path, '/?second')
        self.assertEqual(len(fixture.requests), 2)
        self.assertEqual(fixture.requests[0].path, '/?first')
        self.assertEqual(fixture.requests[1].path, '/?second')

    @FakeServer.run(['hello', 'goodbye'])
    def test_multiple_fixtures_requests(self, fake_server):
        """
        Requests to a running FixtureManager for different fixtures
            receive response from appropriate endpoint
            collects separate requests
        """
        # Make our requests
        res1 = requests.get('http://localhost:9000/?first')
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.text, 'world')

        res2 = requests.get('http://localhost:9000/goodbye?second')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.text, 'moon')

        # Assert we have information in our requests from `httpretty` context
        self.assertEqual(httpretty_fixtures.first_request().path, '/?first')
        self.assertEqual(httpretty_fixtures.last_request().path, '/goodbye?second')
        self.assertEqual(len(httpretty_fixtures.requests()), 2)
        self.assertEqual(httpretty_fixtures.requests()[0].path, '/?first')
        self.assertEqual(httpretty_fixtures.requests()[1].path, '/goodbye?second')

        # Assert we have information in our requests from fixture context
        fixture1 = fake_server.hello
        self.assertEqual(fixture1.first_request.path, '/?first')
        self.assertEqual(fixture1.last_request.path, '/?first')
        self.assertEqual(len(fixture1.requests), 1)
        self.assertEqual(fixture1.requests[0].path, '/?first')

        fixture2 = fake_server.goodbye
        self.assertEqual(fixture2.first_request.path, '/goodbye?second')
        self.assertEqual(fixture2.last_request.path, '/goodbye?second')
        self.assertEqual(len(fixture2.requests), 1)
        self.assertEqual(fixture2.requests[0].path, '/goodbye?second')

    @CounterServer.run(['counter'])
    def test_state_preserved(self, counter_server):
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

    @CounterServer.run(['counter'])
    def test_state_disjoint(self, counter_server):
        """
        A separately running FixtureManager
            does not receive state from past runs
        """
        # Verifies that we don't get bleed from `test_state_preserved`
        res = requests.get('http://localhost:9000/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, '1')

    def test_nesting(self):
        """
        When nesting calls to FixtureManager.start
            we keep HTTPretty enabled until the last FixtureManager is stopped
        """
        # We have not started yet
        self.assertEqual(httpretty.is_enabled(), False)

        # Start one manager, we get a `nested_count = 1`
        CounterServer.start(['counter'])
        self.assertEqual(httpretty.is_enabled(), True)

        # Start a second manager, we get a `nested_count = 2`
        FakeServer.start(['hello'])
        self.assertEqual(httpretty.is_enabled(), True)

        # We stop the second manager, which gets us `nested_count = 1`
        # As well, HTTPretty should still be running
        FakeServer.stop()
        self.assertTrue(httpretty.is_enabled())

        # We stop our last manager, which gives us `nested_count = 0`
        CounterServer.stop()

        # We finally stop HTTPretty since the last fixture manager is stopped
        self.assertFalse(httpretty.is_enabled())

    def test_httpretty_enabled_outside_fixture_manager(self):
        """
        When HTTPretty was started outside of FixtureManager
            we do not disable HTTPretty when the last FixtureManager is stopped
        """
        # Start HTTPretty manually
        httpretty.enable()
        self.assertEqual(httpretty.is_enabled(), True)

        # Start one of our FixtureManagers
        FakeServer.start(['hello'])
        self.assertEqual(FakeServer.httpretty_enabled_at_start, True)
        self.assertEqual(httpretty.is_enabled(), True)

        # Stop out FixtureManger and ensure HTTPretty is still running
        FakeServer.stop()
        self.assertEqual(FakeServer.nested_count, 0)
        self.assertEqual(httpretty.is_enabled(), True)

        # Disable HTTPretty manually and ensure it is stopped
        httpretty.disable()
        self.assertEqual(httpretty.is_enabled(), False)
