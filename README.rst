httpretty-fixtures
==================

.. image:: https://travis-ci.org/underdogio/httpretty-fixtures.png?branch=master
   :target: https://travis-ci.org/underdogio/httpretty-fixtures
   :alt: Build Status

Fixture manager for httpretty

Getting Started
---------------
Install the module with: ``pip install httpretty_fixtures``

.. code:: python

    from httpretty_fixtures import run
    run()

    # Set up our fixture manager
    class FakeElasticsearch(FixtureManager):
        # TODO: Look up the URN that Python uses in ``urlparse``
        __base_url__ = 'http://localhost:9200'

        # TODO: Can we concatenate regexp's or do we have an annoying mess on our hands
        # TODO: Otherwise, we will require passing in full URL here. Maybe with a `.format` for simplicity.
        @get(re.compile('/my_index/my_document/my_id$'))
        def es_index(self, request, uri, res_headers):
            return (200, res_headers, {
                '_index': 'my_index',
                '_type': 'my_document',
                '_id': 'my_id',
                '_version': 1,
                'found': True,
            })

    # Define our tests
    class MyTestCase(unittest.TestCase):
        @FakeElasticsearch.run(['es_index'])
        def test_retrieve_from_es(self):
            """Verify we can retrieve an item from Elasticsearch"""
            res = requests('http://localhost:9200/my_index/my_document/my_id')


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
