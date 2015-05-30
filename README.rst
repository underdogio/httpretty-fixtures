httpretty-fixtures
==================

.. image:: https://travis-ci.org/underdogio/httpretty-fixtures.png?branch=master
   :target: https://travis-ci.org/underdogio/httpretty-fixtures
   :alt: Build Status

Fixture manager for `httpretty`_

This was written to solve communicating to an Elasticsearch during tests. For our usage, ``mock`` didn't scale well and placing `httpretty`_ fixtures on our base test case was impratical. To solve this, we wrote a fixture manager, ``httpretty-fixtures``.

# TODO: Create issue about adding support for receiving server as parameter from decorator and getting `first_request`, `last_request`, and `requests`
# TODO: Build a start/stop and __enter__/__exit__ for manual setup/teardown and `with` context management
#   Never mind, we can prob skip `with` in the initial release
# TODO: We should document that `latest_requests` is used for all of our request accessors
#   and document that if `httpretty` is being used in any other variation, then those requests will appear there as well
# TODO: Provide an example where we preserve state via `__init__`. Be sure to call super there.
# TODO: Assert that 2 separate FixtureManager's don't share the same fixture store
#   https://docs.python.org/2/tutorial/classes.html#private-variables-and-class-local-references

.. _`httpretty`: https://github.com/gabrielfalcao/HTTPretty

Getting Started
---------------
Install the module with: ``pip install httpretty_fixtures``

.. code:: python

    # Load in our dependencies
    import httpretty_fixtures
    import json


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
            res = requests('http://localhost:9200/my_index/my_document/my_id')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json['_index'], 200)

            # Introspect our request received on `FakeElasticsearch`
            self.assertEqual(httpretty_fixtures.first_request.path, '/my_index/my_document/my_id')
            self.assertEqual(httpretty_fixtures.last_request.path, '/my_index/my_document/my_id')
            self.assertEqual(len(httpretty_fixtures.requests), 1)
            self.assertEqual(httpretty_fixtures.requests[0].path, '/my_index/my_document/my_id')

Documentation
-------------
_(Coming soon)_

Examples
--------
_(Coming soon)_

Contributing
------------
In lieu of a formal styleguide, take care to maintain the existing coding style. Add unit tests for any new or changed functionality. Test via ``nosetests``.

License
-------
Copyright (c) 2015 Underdog.io

Licensed under the MIT license.
