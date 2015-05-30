#!/usr/bin/env bash
# Exit on the first error
set -e

# Run our tests
nosetests httpretty_fixtures/test/*.py $*
