from unittest import TestCase
from httpretty_fixtures import httpretty_fixtures


class TestRunFunction(TestCase):
    def test_run_exists(self):
        self.assertTrue(bool(httpretty_fixtures.run))
