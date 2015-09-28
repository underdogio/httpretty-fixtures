# Load in our dependencies
import functools

from httpretty import HTTPretty


# Define our class
class FixtureManager(object):
    # Store a count for HTTPretty across all classes
    nested_count = 0

    @classmethod
    def generate_saving_fixture(cls, fixture):
        """
        Wrap a fixture function with saving functionality

        :param function fixture: Fixture to add saving to
        :rtype: function
        :return: `fixture` with wrapped saving (e.g. saves `first_request`)
        """
        # Wrap our fixture to save request information
        @functools.wraps(fixture)
        def saving_fixture(request, *args, **kwargs):
            # If this is the first request, save it
            if saving_fixture.first_request is None:
                saving_fixture.first_request = request

            # Save the last request
            saving_fixture.last_request = request

            # Add our request onto the stack
            saving_fixture.requests.append(request)

            # Return our normal function
            return fixture(request, *args, **kwargs)

        # Define default information
        saving_fixture.first_request = None
        saving_fixture.last_request = None
        saving_fixture.requests = []

        # Return our saving fixture
        return saving_fixture

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

        # Process our function being decorated
        #   This is the second stage where the `@` of the decorator runs over `test_request_hello`
        #   i.e. `decorate_fn(test_request_hello)`
        def decorate_fn(fn):
            # Wrap our normal function with before/after pieces
            #   `functools.wraps` transfers internals like `__name__` and `__doc__`
            @functools.wraps(fn)
            def wrapper(that_self, *args, **kwargs):
                # Start our class
                server = cls.start(fixtures)

                # Run our fn and always cleanup
                # DEV: We use same function signature as `mock.patch` meaning we append to `args`
                #   https://github.com/calvinchengx/python-mock/blob/5f551e96f48a61fad7617df0d284e003a3eb9a90/mock.py#L1220-L1224
                args += (server,)
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
        # If we can't iterate over our fixtures, complain and leave
        if not hasattr(fixtures, '__iter__'):
            raise TypeError('Expected `fixtures` to be an iterable sequence but it was not. '
                            'Please make it a list or a tuple.')

        # Increase our internal counter
        cls.nested_count += 1

        # If HTTPretty hasn't been started yet, then reset its info and start it
        if not HTTPretty.is_enabled():
            HTTPretty.reset()
            HTTPretty.enable()

        # Initialize our class
        instance = cls()

        # Start each of our fixtures
        # DEV: We must use a separate function to closure `fixture` to prevent reuse in loops
        for fixture_key in fixtures:
            instance.start_fixture(fixture_key)

        # Return our generated server
        return instance

    def start_fixture(self, fixture_key):
        """
        Begin an instance-bound fixture on this instance on HTTPretty

        :param str fixture_key: Name of fixture to start
        """
        # Retrieve our fixture
        fixture = getattr(self, fixture_key)

        # If it is not a function, complain and leave
        if not fixture or not hasattr(fixture, '__call__'):
            raise RuntimeError('Expected fixture "{fixture}" to be a function but it was not.'
                               .format(fixture=fixture_key))

        # If it is not marked as a fixture
        if fixture._httpretty_fixtures_fixture is not True:
            raise RuntimeError('Expected fixture "{fixture}" to be marked as a fixture. '
                               'Please invoke `_httpretty_fixtures.mark_fixture` before using `.run()`/`.start()`'
                               .format(fixture=fixture_key))

        # Generate our saving fixture
        saving_fixture = self.generate_saving_fixture(fixture)

        # Save our new fixture on the instance itself
        # DEV: This prevents leaking out to the class' methods
        setattr(self, fixture_key, saving_fixture)

        # Bind our fixture
        HTTPretty.register_uri(*fixture._httpretty_fixtures_args, body=saving_fixture,
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


# Define our registration methods
# https://github.com/gabrielfalcao/HTTPretty/blob/0.8.3/httpretty/http.py#L112-L121
def mark_fixture_function(fn, *register_uri_args, **register_uri_kwargs):
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


def mark_fixture(*register_uri_args, **register_uri_kwargs):
    """
    Decorator wrapper for `mark_fixture_function`

    :param *args register_uri_args: Arguments to pass through to `httpretty.register_uri`
    :param **kwargs register_uri_kwargs: Keyword arguments to pass through to `httpretty.register_uri`
    """
    def mark_fixture_decorator(fn):
        # Process our function via `mark_fixture_function` and return it
        return mark_fixture_function(fn, *register_uri_args, **register_uri_kwargs)
    return mark_fixture_decorator


# Define helper registration methods for each HTTP verb
get = functools.partial(mark_fixture, HTTPretty.GET)
put = functools.partial(mark_fixture, HTTPretty.PUT)
post = functools.partial(mark_fixture, HTTPretty.POST)
delete = functools.partial(mark_fixture, HTTPretty.DELETE)
head = functools.partial(mark_fixture, HTTPretty.HEAD)
patch = functools.partial(mark_fixture, HTTPretty.PATCH)
options = functools.partial(mark_fixture, HTTPretty.OPTIONS)
connect = functools.partial(mark_fixture, HTTPretty.CONNECT)


# Create aliases for httpretty's requests
def first_request():
    """Retreive the first request encountered by HTTPretty"""
    # If there is at least 1 request, return the first one
    if HTTPretty.latest_requests:
        return HTTPretty.latest_requests[0]


def last_request():
    """Retreive the last request encountered by HTTPretty"""
    # If there is at least 1 request, return the last one
    latest_requests = HTTPretty.latest_requests
    if latest_requests:
        return latest_requests[len(latest_requests) - 1]


def requests():
    """Retrieve all requests encountered by HTTPretty"""
    return HTTPretty.latest_requests
