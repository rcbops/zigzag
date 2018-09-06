# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
pytest_plugins = ['helpers_namespace', 'tests.helper.fixtures']


# ======================================================================================================================
# Public Fixtures: Meant to be consumed by tests
# ======================================================================================================================
@pytest.fixture(scope='session')
def single_passing_test_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with one passing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_passing_asc.xml', 'asc')
    zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def single_passing_test_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with one passing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_passing_mk8s.xml', 'mk8s')
    zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def single_failing_test_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with one failing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_failing_asc.xml', 'asc')
    zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def single_failing_test_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with one failing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_failing_mk8s.xml', 'mk8s')
    zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_passing_tests_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 passing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_passing_asc.xml', 'asc')
    for i in range(3):
        zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_passing_tests_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 passing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_passing_mk8s.xml', 'mk8s')
    for i in range(3):
        zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_failing_tests_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 failing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_failing_asc.xml', 'asc')
    for i in range(3):
        zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_failing_tests_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 failing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_failing_mk8s.xml', 'mk8s')
    for i in range(3):
        zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_erroring_tests_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 erroring tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_erroring_asc.xml', 'asc')
    for i in range(3):
        zz_runner.add_test_case('error')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_erroring_tests_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 erroring tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_erroring_mk8s.xml', 'mk8s')
    for i in range(3):
        zz_runner.add_test_case('error')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_skipping_tests_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 skipping tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_skipping_asc.xml', 'asc')
    for i in range(3):
        zz_runner.add_test_case('skipped')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_skipping_tests_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 skipping tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_skipping_mk8s.xml', 'mk8s')
    for i in range(3):
        zz_runner.add_test_case('skipped')

    return zz_runner


@pytest.fixture(scope='session')
def mixed_status_tests_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with 4 tests covering the various test execution
     states in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_mixed_asc.xml', 'asc')
    for state in ('passed', 'failure', 'error', 'skipped'):
        zz_runner.add_test_case(state)

    return zz_runner


@pytest.fixture(scope='session')
def mixed_status_tests_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 4 tests covering the various test execution
     states in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_mixed_mk8s.xml', 'mk8s')
    for state in ('passed', 'failure', 'error', 'skipped'):
        zz_runner.add_test_case(state)

    return zz_runner


@pytest.fixture(scope='session')
def single_passing_test_step_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with a test case containing one passing test step.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_passing_test_step_for_asc.xml', 'asc')
    zz_runner.add_test_case('passed', test_steps=[{'state': 'passed'}])

    return zz_runner


@pytest.fixture(scope='session')
def single_passing_test_step_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with a test case containing one passing test step.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_passing_test_step_for_mk8s.xml', 'mk8s')
    zz_runner.add_test_case('passed', test_steps=[{'state': 'passed'}])

    return zz_runner
