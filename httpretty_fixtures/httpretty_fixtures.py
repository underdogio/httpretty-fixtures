# Load in our dependencies
import functools

from httpretty import HTTPretty


# Define our class
class FixtureManager(object):
    # Store a count for HTTPretty
    nested_count = 0

    # Store a per-class set of fixtures (changes between inherited instances)
    # https://docs.python.org/2/tutorial/classes.html#private-variables-and-class-local-references
    __fixtures = {}

    @classmethod
    def run(cls, fixtures):
        """
        Decorator to start up `httpretty` with a set of fixtures

        :param list fixtures: Names of fixtures to load onto `httpretty`
        """
        # For helping with logic, here is an example of what every part is
        # @FakeElasticsearch.run(['hello'])
        # def test_request_hello(self, arg1, arg2):
        #   pass

        # `cls` is `FakeElasticsearch`
        # `fixtures` is `['hello']`
        # We are initially executing `FakeElasticsearch.run(['hello'])` as if were a function

        # If we can't iterate over our fixtures, complain and leave
        if not hasattr(fixtures, '__iter__'):
            raise TypeError('Expected `fixtures` to be an iterable sequence but it was not. '
                            'Please make it a list or a tuple.')

        # Process our
        # This is the second stage where the `@` of the decorator runs over `test_request_hello`
        #   i.e. `decorate_fn(test_request_hello)`
        def decorate_fn(fn):
            # Wrap our normal function with before/after pieces
            #   `functools.wraps` transfers internals like `__name__` and `__doc__`
            @functools.wraps(fn)
            def wrapper(self, *args, **kwargs):
                # Start our class
                cls.start()

                # Run our fn and always cleanup
                try:
                    return fn(self, *args, **kwargs)
                finally:
                    cls.stop()

            # Return our wrapped function
            #   i.e. `test_request_hello` with some before/after logic (of start/stop)
            return wrapper

        # Return our decorator to process our function
        #  i.e. `decorator_fn` to process `test_request_hello`
        return decorate_fn

    @classmethod
    def save_fixture(cls, name, *register_uri_args, **register_uri_kwargs):
        """
        Save a fixture to our class for usage later on

        :param str name: Key to store fixture under
        :param *args register_uri_args: Arguments to pass through to `httpretty.register_uri`
        :param **kwargs register_uri_kwargs: Keyword arguments to pass through to `httpretty.register_uri`
        """
        # If there already is a fixture, complain
        if name in cls.__fixtures:
            raise RuntimeError('Key "{name}" already exists in fixtures for `httpretty-fixtures`'.format(name=name))

        # Otherwise, save our fixture
        cls.__fixtures[name] = {
            'args': register_uri_args,
            'kwargs': register_uri_kwargs,
        }

    # https://github.com/gabrielfalcao/HTTPretty/blob/0.8.3/httpretty/core.py#L1023-L1032
    # https://github.com/spulec/moto/blob/0.4.2/moto/core/models.py#L32-L65
    def start(cls):
        """Start running this class' fixtures"""
        # Increase our internal counter
        cls.nested_count += 1

        # If HTTPretty hasn't been started yet, then reset its info start it
        if not HTTPretty.is_enabled():
            HTTPretty.enable()

        # For each of our fixtures, bind them
        for name in cls.__fixtures:
            fixture = cls.__fixtures[name]
            HTTPretty.register_uri(*fixture['args'], **fixture['kwargs'])

    def stop(cls):
        """Stop running this class' fixtures"""
        # Decrease our counter
        cls.nested_count -= 1

        # If we have stopped running too many times, complain and leave
        if cls.nested_count < 0:
            raise RuntimeError('When running `httpretty-fixtures`, `stop()`'
                               'was run more times than (or before) `start()`')

        # If we have gotten out of nesting, then stop HTTPretty and
        if cls.nested_count == 0:
            HTTPretty.disable()

# Define our helper registration methods
# https://github.com/gabrielfalcao/HTTPretty/blob/0.8.3/httpretty/http.py#L112-L121
_method_map = {
    'GET': 'get',
    'PUT': 'put',
    'POST': 'post',
    'DELETE': 'delete',
    'HEAD': 'head',
    'PATCH': 'patch',
    'OPTIONS': 'options',
}
for httpretty_method in HTTPretty.METHODS:
    @classmethod
    def save_fixture_by_method(cls, fixture_fn, *register_uri_args, **register_uri_kwargs):
        # Register our URL under the fixture's name
        body = fixture_fn
        cls.save_fixture(fixture_fn.__name__, httpretty_method, *register_uri_args, body=body, **register_uri_kwargs)

        # Return our function for reuse
        return fixture_fn
    class_key = _method_map[httpretty_method]
    setattr(FixtureManager, class_key, save_fixture_by_method)
