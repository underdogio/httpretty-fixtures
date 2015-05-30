# Load in our dependencies
from unittest import TestCase

import requests

from httpretty_fixtures import FixtureManager

# TODO: The API is still fucky. We don't have context for `self` anywhere...
# TODO: Is this even possible? Maybe we need to generate an instance outside and then extend it somehow?
#   I don't think it's possible because we need `self's` context but `httpretty` doesn't know that.
#   So we need to somehow bind it such that `self` is invoked somewhere but we lack that context in all scenarios.
#   I think it worked in our internal repo because we had somewhat of a singleton to point to.
#   Or maybe something like: `httpretty_fixtures.run(FakeServer, ['abcdef'])` but that is gnarly

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
