# Load in our dependencies
import json
import unittest

import httpretty_fixtures
import requests


# Set up our fixture manager
class FakeElasticsearch(httpretty_fixtures.FixtureManager):
    @httpretty_fixtures.get('http://localhost:9200/my_index/my_document/my_id')
    def es_index(self, request, uri, res_headers):
        return (200, res_headers, json.dumps({
            '_index': 'my_index',
            '_type': 'my_document',
            '_id': 'my_id',
            '_version': 1,
            'found': True,
        }))


# Define our tests
class MyTestCase(unittest.TestCase):
    @FakeElasticsearch.run(['es_index'])
    def test_retrieve_from_es(self):
        """Verify we can retrieve an item from Elasticsearch"""
        # Make our request and verify we hit Elasticsearch
        res = requests.get('http://localhost:9200/my_index/my_document/my_id')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['_index'], 'my_index')

        # Introspect our request received on `FakeElasticsearch`
        self.assertEqual(httpretty_fixtures.first_request().path, '/my_index/my_document/my_id')
        self.assertEqual(httpretty_fixtures.last_request().path, '/my_index/my_document/my_id')
        self.assertEqual(len(httpretty_fixtures.requests()), 1)
        self.assertEqual(httpretty_fixtures.requests()[0].path, '/my_index/my_document/my_id')


# Run our tests
if __name__ == '__main__':
    unittest.main()
