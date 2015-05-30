# Load in our dependencies
import functools

from httpretty import HTTPretty


# Define our class
class FixtureManager(object):
    # Store a count for HTTPretty across all classes
    nested_count = 0

    @classmethod
    def mark_fixture(cls, fn, *register_uri_args, **register_uri_kwargs):
        """
        Mark a function as a fixture and save its register_uri_args and register_uri_kwargs

        :param function fn: Function to use as our fixture
        :param *args register_uri_args: Arguments to pass through to `httpretty.register_uri`
        :param **kwargs register_uri_kwargs: Keyword arguments to pass through to `httpretty.register_uri`
        """
        # Mark the fixture with our key and save its args/kwargs
        fn._httpretty_fixtures_fixture = True
        fn._httpretty_fixtures_args = register_uri_args
        fn._httpretty_fixtures_kwargs = register_uri_kwargs

        # Return our function
        return fn

    @classmethod
    def run(cls, fixtures):
        """
        Decorator to start up `httpretty` with a set of fixtures

        :param list fixtures: Names of fixtures to load onto `httpretty`
        """
        # For helping with logic, here is an example of what every part is
        # @FakeElasticsearch.run(['hello'])
        # def test_request_hello(cls, arg1, arg2):
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
            def wrapper(that_self, *args, **kwargs):
                # Start our class
                cls.start(fixtures)

                # Run our fn and always cleanup
                try:
                    return fn(that_self, *args, **kwargs)
                finally:
                    cls.stop()

            # Return our wrapped function
            #   i.e. `test_request_hello` with some before/after logic (of start/stop)
            return wrapper

        # Return our decorator to process our function
        #  i.e. `decorator_fn` to process `test_request_hello`
        return decorate_fn

    # https://github.com/gabrielfalcao/HTTPretty/blob/0.8.3/httpretty/core.py#L1023-L1032
    # https://github.com/spulec/moto/blob/0.4.2/moto/core/models.py#L32-L65
    @classmethod
    def start(cls, fixtures):
        """Start running this class' fixtures"""
        # Increase our internal counter
        cls.nested_count += 1

        # If HTTPretty hasn't been started yet, then reset its info start it
        if not HTTPretty.is_enabled():
            HTTPretty.enable()

        # Initialize our class
        instance = cls()

        # For each of our fixtures
        for fixture in fixtures:
            # Retrieve our fixture
            attr = getattr(instance, fixture)

            # If it is function and is marked as a fixture, register it
            if attr and hasattr(attr, '__call__') and attr._httpretty_fixtures_fixture is True:
                # Update the fixture to know about `self`
                fixture = attr
                contextual_fixture = functools.partial(fixture)
                HTTPretty.register_uri(*fixture._httpretty_fixtures_args, body=contextual_fixture,
                                       **fixture._httpretty_fixtures_kwargs)

    @classmethod
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
    HTTPretty.GET: 'get',
    HTTPretty.PUT: 'put',
    HTTPretty.POST: 'post',
    HTTPretty.DELETE: 'delete',
    HTTPretty.HEAD: 'head',
    HTTPretty.PATCH: 'patch',
    HTTPretty.OPTIONS: 'options',
    HTTPretty.CONNECT: 'connect',
}
for httpretty_method in HTTPretty.METHODS:
    # Define a closure for our `httpretty_method`. Otherwise, it's a reference to `CONNECT` indefinitely
    def _save_fixture_by_method(httpretty_method):
        @classmethod
        def save_fixture_by_method(cls, *register_uri_args, **register_uri_kwargs):
            def save_fixture_by_method_decorator(fixture_fn):
                # Register our URL under the fixture's name
                cls.mark_fixture(fixture_fn, httpretty_method,
                                 *register_uri_args, **register_uri_kwargs)

                # Return our function for reuse
                return fixture_fn

            # Return our decorator
            return save_fixture_by_method_decorator
        # Return our closured method
        return save_fixture_by_method
    class_key = _method_map[httpretty_method]
    setattr(FixtureManager, class_key, _save_fixture_by_method(httpretty_method))
