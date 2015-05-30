# Load in our dependencies
import functools

from httpretty import HTTPretty


# Define our class
class FixtureManager(object):
    # Store a count for HTTPretty across all classes
    nested_count = 0

    def run(self, fixtures):
        """
        Decorator to start up `httpretty` with a set of fixtures

        :param list fixtures: Names of fixtures to load onto `httpretty`
        """
        # For helping with logic, here is an example of what every part is
        # @FakeElasticsearch.run(['hello'])
        # def test_request_hello(self, arg1, arg2):
        #   pass

        # `self` is `FakeElasticsearch`
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
                self.start()

                # Run our fn and always cleanup
                try:
                    return fn(that_self, *args, **kwargs)
                finally:
                    self.stop()

            # Return our wrapped function
            #   i.e. `test_request_hello` with some before/after logic (of start/stop)
            return wrapper

        # Return our decorator to process our function
        #  i.e. `decorator_fn` to process `test_request_hello`
        return decorate_fn

    def mark_fixture(self, fn, *register_uri_args, **register_uri_kwargs):
        """
        Mark a function as a fixture and save its register_uri_args and register_uri_kwargs

        :param function fn: Function to use as our fixture
        :param *args register_uri_args: Arguments to pass through to `httpretty.register_uri`
        :param **kwargs register_uri_kwargs: Keyword arguments to pass through to `httpretty.register_uri`
        """
        # Mark the fixture with our key and save its args/kwargs
        fn._httpretty_fixtures_fn = True
        fn._httpretty_fixtures_args = register_uri_args
        fn._httpretty_fixtures_kwargs = register_uri_kwargs

    # https://github.com/gabrielfalcao/HTTPretty/blob/0.8.3/httpretty/core.py#L1023-L1032
    # https://github.com/spulec/moto/blob/0.4.2/moto/core/models.py#L32-L65
    def start(self):
        """Start running this class' fixtures"""
        # Increase our internal counter
        self.nested_count += 1

        # If HTTPretty hasn't been started yet, then reset its info start it
        if not HTTPretty.is_enabled():
            HTTPretty.enable()

        # For each of our fixtures, bind them
        for name in self._fixtures:
            fixture = self._fixtures[name]
            HTTPretty.register_uri(*fixture['args'], **fixture['kwargs'])

    def stop(self):
        """Stop running this class' fixtures"""
        # Decrease our counter
        self.nested_count -= 1

        # If we have stopped running too many times, complain and leave
        if self.nested_count < 0:
            raise RuntimeError('When running `httpretty-fixtures`, `stop()`'
                               'was run more times than (or before) `start()`')

        # If we have gotten out of nesting, then stop HTTPretty and
        if self.nested_count == 0:
            HTTPretty.disable()


# Define our helper registration methods
# https://github.com/gabrielfalcao/HTTPretty/blob/0.8.3/httpretty/http.py#L112-L121

get = FixtureManager.HTTPretty.GET
put = FixtureManager.HTTPretty.PUT
post = FixtureManager.HTTPretty.POST
delete = FixtureManager.HTTPretty.DELETE
head = FixtureManager.HTTPretty.HEAD
patch = FixtureManager.HTTPretty.PATCH
options = FixtureManager.HTTPretty.OPTIONS
connect = FixtureManager.HTTPretty.CONNECT
