httpretty-fixtures
==================

.. image:: https://travis-ci.org/underdogio/httpretty-fixtures.png?branch=master
   :target: https://travis-ci.org/underdogio/httpretty-fixtures
   :alt: Build Status

Fixture manager for `httpretty`_

**Features:**

- Reuse responses across tests
- Allows maintaining state between requests

  - See the `Examples section for a demonstration <#preserving-state-between-requests>`_

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
``httpretty-fixtures`` exports ``FixtureManager``, ``get``, ``put``, ``post``, ``delete``, ``head``, ``patch``, ``options``, ``connect``, ``first_request``, ``last_request``, and ``requests`` as methods/variables.

We will refer to the package as ``httpretty_fixtures``.

FixtureManager()
^^^^^^^^^^^^^^^^
Class for setting up a set of fixtures on. This should be inherited from into another class with its own set of fixtures.

.. code:: python
    class FakeElasticsearch(httpretty_fixtures.FixtureManager):
        @httpretty_fixtures.get('http://localhost:9200/my_index/my_document/my_id')
        def es_index(self, request, uri, res_headers):
            return (200, res_headers, json.dumps({'content': 'goes here'}))


fixture_manager.run(fixtures)
"""""""""""""""""""""""""""""
Decorator to run a set of fixtures during a function

- fixtures ``list`` - Names of fixture functions to run

  - \* ``str`` - Name of fixtures function to run

.. code:: python
    class FakeElasticsearch(httpretty_fixtures.FixtureManager):
        @httpretty_fixtures.get('http://localhost:9200/my_index/my_document/my_id')
        def es_index(self, request, uri, res_headers):
            return (200, res_headers, json.dumps({}))

    class MyTestCase(unittest.TestCase):
        # The `es_index` fixture will be live for all of this test case
        @FakeElasticsearch.run(['es_index'])
        def test_retrieve_from_es(self):
            """Verify we can retrieve an item from Elasticsearch"""
            # Make our request and verify we hit Elasticsearch
            res = requests.get('http://localhost:9200/my_index/my_document/my_id')

fixture_manager.start(fixtures)
"""""""""""""""""""""""""""""""
Start running HTTPretty with a set of fixtures

- fixtures ``list`` - Names of fixture functions to run

  - \* ``str`` - Name of fixtures function to run


This will run HTTPretty indefinitely until ``.stop()`` is run

fixture_manager.stop()
""""""""""""""""""""""
Stop a running instance of HTTPretty. This should always be run at some point after a ``.start()``

httpretty_fixtures.{verb}(\*register_uri_args, \*\*register_uri_kwargs)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Decorator to register a fixture function under an HTTP verb

This is a summary for all possible HTTP verbs:

.. code:: python

    @httpretty_fixtures.get()
    @httpretty_fixtures.put()
    @httpretty_fixtures.post()
    @httpretty_fixtures.delete()
    @httpretty_fixtures.head()
    @httpretty_fixtures.patch()
    @httpretty_fixtures.options()
    @httpretty_fixtures.connect()

Each of these verbs functions passes its arguments/keyword arguments to ``HTTPretty's register_uri` function``.

If there are any arguments you want to apply to your fixture with respect to ``HTTPretty``, this is how to do it.

https://github.com/gabrielfalcao/HTTPretty/tree/0.8.3#usage

.. code:: python

    @httpretty_fixtures.get("http://underdog.io/")

Function signature
""""""""""""""""""
``httpretty_fixtures`` leverages the dynamic callback functionality of ``httpretty``:

https://github.com/gabrielfalcao/HTTPretty/tree/0.8.3#dynamic-responses-through-callbacks

As a result, we expect our decorator to receive a function that matches the following signature:

.. code:: python

    @httpretty_fixtures.get("http://underdog.io/")
    def request_handler(self, request, uri, res_headers):
        res_tuple = (status_code, res_headers, body)
        return res_tuple

    # Example
    @httpretty_fixtures.get("http://underdog.io/")
    def hello(self, request, uri, res_headers):
        return (200, res_headers, 'Hello World!')

The signature is as follows:

- request_handler ``function`` - Handler for our request callback
- self ``object`` - Instance of class extended on top of for ``FixtureManager``
- uri ``object`` - Information about incoming request
    - Structure is managed by ``httpretty``
    - More info can be read from the source code
        - https://github.com/gabrielfalcao/HTTPretty/blob/0.8.3/httpretty/core.py#L615-L647
- res_headers ``object`` - Default response headers to provide to request
    - These should be modified and/or passed through in the `res_tuple`
- res_tuple ``tuple`` - Collection of information for our response
    - [0] ``int`` - Status code to provide for response
        - For example, 200 would be a 200 HTTP status code
    - [1] ``object`` - Modified or provided set of headers provided as a parameter
    - [2] ``str`` - Response body for our request
        - In the example above, we replied with ``'Hello World!'`` but this could be JSON, XML, or whatever you need

httpretty_fixtures.first_request()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Alias to access the first request received by ``HTTPretty``.

**Warning:** If you are using ``HTTPretty`` in other locations, then this will register those requests as well.

httpretty_fixtures.last_request()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Alias to access the last request received by ``HTTPretty``.

**Warning:** If you are using ``HTTPretty`` in other locations, then this will register those requests as well.

httpretty_fixtures.requests()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Alias to access all requests received by ``HTTPretty``.

**Warning:** If you are using ``HTTPretty`` in other locations, then this will register those requests as well.

Examples
--------
Preserving state between requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this example, we will count between multiple requests to indicate that state is being preserved.

.. code:: python

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

Contributing
------------
In lieu of a formal styleguide, take care to maintain the existing coding style. Add unit tests for any new or changed functionality. Test via ``nosetests``.

License
-------
Copyright (c) 2015 Underdog.io

Licensed under the MIT license.
