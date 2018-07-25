===================
Integration Testing
===================

This document covers how to write and execute ``ZigZag`` integration tests.

Test Components
---------------

The `conftest.py`_ for integration testing contains the following fixtures, classes and functions utilized by the
integration test layer. The test classes are used to control state and provide functionality for publishing and
validation of data in the qTest project under test. The test fixtures wrap the test classes to provide ``pytest`` setup
and teardown functionality.

Classes
^^^^^^^

- ``TestCaseInfo``
    This class models a single JUnitXML style test case produced by the `pytest-rpc`_ plug-in. The class provides
    properties that map to the data attributes found in a JUnitXML style test case produced by the `pytest-rpc`_
    plug-in. Methods on the class can be used to validate state on the qTest project under test.
- ``TestSuiteInfo``
    This container class models a JUnitXML style test suite produced by the `pytest-rpc`_ plug-in. The class provides
    properties that map to the data attributes found in a JUnitXML style test suite produced by the `pytest-rpc`_
    plug-in. The ``add_test_case`` method will add ``TestCaseInfo`` objects to the internal data structure.
- ``ZigZagRunner``
    This class does the heavy lifting when it comes to invoking ``ZigZag`` against JUnitXML result files built on the
    fly. This class wraps the ``TestSuiteInfo`` class and provides pass-through methods for accessing the critical
    ``TestSuiteInfo`` methods needed for modeling a proper JUnitXML test result file produced by the `pytest-rpc`_
    plug-in.

Fixtures
^^^^^^^^

- ``_configure_test_environment``
    This private fixture is used to prepare the qTest project under test for testing. This fixture is responsible for
    doing the final clean-up of test cycle artifacts after the `pytest`_ session completes.
- ``qtest_env_vars``
    Retrieve a dictionary of required environment variables for running integration tests. If the required environment
    variables are not present then this fixture will force all tests to fail. (Be aware that the failure message from
    this fixture is obtuse! Just remember that you need "QTEST_API_TOKEN" and "QTEST_SANDBOX_PROJECT_ID" environment
    variables populated if this fixture fails.)
- ``_zigzag_runner_factory``
    This private fixture factory is used as the basis for representing JUnitXML test result files produced by the
    `pytest-rpc`_ plug-in. This fixture is responsible for doing the final clean-up of test module artifacts after the
    `pytest`_ session completes.

Helpers
^^^^^^^

- ``_search_qtest``
    Search qTest for objects matching a given query. (This helper exists because the swagger_client search API
    returns a really useless model.)

Workflow for Writing a Test Case
--------------------------------

This section covers the best practices for implementing test cases at the integration layer. This section assumes that
the developer is already familiar with how to write high quality `pytest`_ test cases.

Selecting a Starting Fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since ``ZigZag`` is all about consuming JUnitXML result files to publish to qTest, the first step is to select/create a
fixture that represents the desired test run session results you're trying to validate. The ``Public Fixtures`` section
of `conftest.py`_ contains all the shared fixtures meant to be used by test cases. Developers are encouraged to first
scour the available fixtures to discover if one exists that covers the scenario that is under development for a given
test case.

Creating a Starting Fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If an appropriate test fixture does not already exist that fits your test scenario then follow these steps to create
one!

#. Create a fixture that inherits from ``_zigzag_runner_factory`` and is scoped to live for the whole test session::

    @pytest.fixture(scope='session')
    def a_bunch_of_failures(_zigzag_runner_factory):
        # code

#. Invoke a ``ZigZagRunner`` from the factory with a **unique** file name along with the desired CI environment to emulate::

    zz_runner = _zigzag_runner_factory('a_bunch_of_failures.xml', 'asc')

#. Add test cases with desired attributes. (See ``TestCaseInfo`` for more details) ::

    zz_runner.add_test_case('failed')
    zz_runner.add_test_case('failed')
    zz_runner.add_test_case('failed')

#. Make sure to return the runner to the caller::

    return zz_runner

Building a Test Case with a Fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once a fixture has been selected/created, then you need to inherit the fixture for your test case::

    def test_a_bunch_of_failures(a_bunch_of_failures):
        # code

Invoking ZigZag
^^^^^^^^^^^^^^^

To invoke ``ZigZag`` use::

    a_bunch_of_failures.assert_invoke_zigzag()

Or use::

    a_bunch_of_failures.invoke_zigzag()

The suggested method to use is ``assert_invoke_zigzag`` because it will do automatic basic validation that the test
case exists after invoking ``ZigZag``. The ``invoke_zigzag`` method should only be used when attempting to validate
a negative scenario or more fine grained control is needed when validating state in qTest.

Clean-up
^^^^^^^^

The ``_configure_test_environment`` and ``_zigzag_runner_factory`` private fixtures already perform clean-up duties
during test run session teardown. However, sometimes it is necessary to clean-up artifacts during test case execution.
The ``TestCaseInfo``, ``TestSuiteInfo`` and ``ZigZagRunner`` classes all provide a ``clean_up`` method which will
remove artifacts. Use the ``clean_up`` with caution because misuse *could* cause teardown in upstream fixtures to fail
in bizarre ways. Basically, these knives are sharp and they will cut you.

Validation
^^^^^^^^^^

The ``TestCaseInfo``, ``TestSuiteInfo`` and ``ZigZagRunner`` classes all provide some basic ``assert`` methods for
state validation. For complex test scenarios the state of artifacts in the qTest project under test will need to be
done using the `qTest swagger client`_ by the developer. FYI, the ``ZigZagRunner`` class provides properties that can
be quite helpful in assisting with validation using the `qTest swagger client`_ Python package.

Executing Integration Tests
---------------------------

As a prerequisite to running the integration tests the following environment variables must be set:

- ``QTEST_API_TOKEN``
    Your *personal* API token. (**DO NOT EVER USE THE SHARED AUTOMATION TOKEN!!!!!** You will be ridiculed endlessly
    if you do so!)
- ``QTEST_SANDBOX_PROJECT_ID``
    The qTest project ID for the sandbox project. (**DO NOT USE A PRODUCTION PROJECT ID!!!!!** May the computer gods
    show you no mercy if you ever do this.)

Once the appropriate environment variables are set, you can execute the integration tests using the handy-dandy ``make``
task::

    $ make test-integration


.. _conftest.py: ../tests/integration/conftest.py
.. _pytest-rpc: https://github.com/rcbops/pytest-rpc
.. _pytest: https://docs.pytest.org/en/latest/index.html
.. _qTest swagger client: https://github.com/rcbops/qtest-swagger-client