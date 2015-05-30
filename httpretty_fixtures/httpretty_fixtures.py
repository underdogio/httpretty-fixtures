# Load in our dependencies
from httpretty import httpretty


# Define our class
class FixtureManager(object):
    # Store a per-class set of fixtures (changes between inherited instances)
    # https://docs.python.org/2/tutorial/classes.html#private-variables-and-class-local-references
    __fixtures = {}

    @classmethod
    def run(cls, fixtures):
        """
        Decorator to start up `httpretty` with a set of fixtures

        :param list fixtures: Names of fixtures to load onto `httpretty`
        """
        # If we can't iterate over our fixtures, complain and leave
        if not hasattr(fixtures, '__iter__'):
            raise TypeError('Expected `fixtures` to be an iterable sequence but it was not. '
                            'Please make it a list or a tuple.')

        # TODO: Copy setup/teardown from moto

        # Define our decorator
        # https://github.com/gabrielfalcao/HTTPretty/blob/0.8.3/httpretty/core.py#L1023-L1032
        def decorate_callable(fn):
            @functools.wraps(fn)
            def wrapper(self, *args, **kwargs):
                # Reset past fixtures
                httpretty.reset()
                httpretty.enable()

                # Iterate and activate each of our fixtures
                http_fixtures = HttpFixtures()
                for fixture in fixtures:
                    fixture_fn = getattr(http_fixtures, fixture)
                    fixture_fn()

                # Save http_fixtures to `self`
                self.http_fixtures = http_fixtures

                # Run our fn and always cleanup
                try:
                    return fn(self, *args, **kwargs)
                finally:
                    httpretty.disable()
            return wrapper
        return decorate_callable

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
for httpretty_method in httpretty.METHODS:
    @classmethod
    def save_fixture_decorator(cls, fixture_fn, *register_uri_args, **register_uri_kwargs):
        # Register our URL under the fixture's name
        cls.save_fixture(fixture_fn.__name__, httpretty_method, *register_uri_args, **register_uri_kwargs)

        # Return our function for reuse
        return fixture_fn
    class_key = _method_map[httpretty_method]
    setattr(FixtureManager, class_key, save_fixture_decorator)
