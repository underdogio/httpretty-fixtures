# Load in our dependencies
from httpretty import httpretty


# Define our class
class FixtureManager(object):
    @classmethod
    def run(cls, fixtures):
        """
        Decorator factory to enable HTTP fixtures for test case

            @run(['es_index'])

        :param list fixtures: Names of fixtures to load onto `httpretty`
        """
        if not hasattr(fixtures, '__iter__'):
            raise TypeError('Expected `fixtures` to be an iterable sequence but it was not. '
                            'Please make it a list or a tuple.')

        # TODO: Copy setup/teardown from moto

        # Define our decorator
        # https://github.com/gabrielfalcao/HTTPretty/blob/0.8.3/httpretty/core.py#L1023-L1032
        def decorate_callable(test):
            @functools.wraps(test)
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

                # Run our test and always cleanup
                try:
                    return test(self, *args, **kwargs)
                finally:
                    httpretty.disable()
            return wrapper
        return decorate_callable

# Define our registration methods
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
