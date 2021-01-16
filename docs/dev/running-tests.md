# Running Onionr tests

Onionr has four types of tests:

* unittests
* integration tests
* selenium tests (web tests)
* runtime-tests


## unittests

Onionr uses Python's built in unittest module. These tests are located in tests/ (top level)

Run all tests with `$ make test`, which will also run integration tests.

Please note that one unittest tests if runtime-tests have passed recently. This is simply a forceful reminder to run those tests as well.

You can also run a single unittest in a loop by using the script scripts/run-unit-test-by-name.py

## integration tests

These tests are pretty basic and test on stdout of Onionr commands.

They are also run from `$ make test`

The runtime-tests do most of the actual integration testing.

## selenium tests

These are browser automation tests to test if the UI is working as how it should for a user.

There's only a couple and they're incomplete, so they can be ignored for now (test manually)

## runtime-tests

These are important. They look into the Onionr client Flask app when Onionr daemon is running and test a bunch of things.

If you do it a lot you should make your own Onionr network (disable official bootstrap)

You run this while the daemon is running (probably should make sure onboarding is done), with `$ onionr.sh runtime-test`

It's necessary to do this before running `$ make test` for unittesting

