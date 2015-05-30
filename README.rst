httpretty-fixtures
==================

.. image:: https://travis-ci.org/underdogio/httpretty-fixtures.png?branch=master
   :target: https://travis-ci.org/underdogio/httpretty-fixtures
   :alt: Build Status

Fixture manager for `httpretty`_

**Features:**

- Reuse responses across tests
- Allows maintaining state between requests
    - See Examples section for a demonstration: :ref:`state-between-requests`
- Access past request information

This was written to solve communicating to an Elasticsearch during tests. For our usage, ``mock`` didn't scale well and placing `httpretty`_ fixtures on our base test case was impratical. To solve this, we wrote a fixture manager, ``httpretty-fixtures``.

.. _`httpretty`: https://github.com/gabrielfalcao/HTTPretty

Getting Started
---------------
Install the module with: ``pip install httpretty_fixtures``

.. code:: python

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


Documentation
-------------
``httpretty-fixtures`` exports ``FixtureManager``, ``get``, ``put``, ``post``, ``delete``, ``head``, ``patch``, ``options``, ``connect``, ``first_request``, ``last_request``, and ``requests`` as methods/variables. We will refer to the package as ``httpretty_fixtures``.

FixtureManager
^^^^^^^^^^^^^^
Class for setting up a set of fixtures on. This should be inherited from into another class with its own set of fixtures.

.. code:: python
    class FakeElasticsearch(httpretty_fixtures.FixtureManager):
        @httpretty_fixtures.get('http://localhost:9200/my_index/my_document/my_id')
        def es_index(self, request, uri, res_headers):
            return (200, res_headers, json.dumps({'content': 'goes here'}))



# TODO: We should document that `latest_requests` is used for all of our request accessors
#   and document that if `httpretty` is being used in any other variation, then those requests will appear there as well

Examples
--------
_(Coming soon)_
# TODO: Provide an example where we preserve state via `__init__`. Be sure to call super there.
#    Make sure we use the ref from Getting Started

Contributing
------------
In lieu of a formal styleguide, take care to maintain the existing coding style. Add unit tests for any new or changed functionality. Test via ``nosetests``.

License
-------
Copyright (c) 2015 Underdog.io

Licensed under the MIT license.
