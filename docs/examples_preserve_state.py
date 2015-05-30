# Load in our dependencies
import unittest

import httpretty_fixtures
import requests


# Set up our fixture manager
class CounterServer(httpretty_fixtures.FixtureManager):
    def __init__(self):
        self.count = 0
        super(CounterServer, self).__init__()

    @httpretty_fixtures.get('http://localhost:9000/')
    def counter(self, request, uri, res_headers):
        self.count += 1
        return (200, res_headers, str(self.count))


# Define our tests
class MyTestCase(unittest.TestCase):
    @CounterServer.run(['counter'])
    def test_counter_state(self):
        """Verify we can preserve state between requests"""
        # Make our first request and verify its count
        res = requests.get('http://localhost:9000/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, '1')

        # Make our second request and verify its count
        res = requests.get('http://localhost:9000/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, '2')


# Run our tests
if __name__ == '__main__':
    unittest.main()
