# -*- coding: utf-8 -*-

"""Tests for validating that test cases with steps are represented correctly in qTest."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
# noinspection PyShadowingNames
@pytest.fixture(scope='module')
def single_skipping_test_step_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with a test case containing one skipping test step.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_skipping_test_step_for_asc.xml', asc_config_file, asc_global_props)
    zz_runner.add_test_case('passed', test_steps=[{'state': 'skipped'}])

    return zz_runner


# noinspection PyShadowingNames
@pytest.fixture(scope='module')
def single_erroring_test_step_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with a test case containing one erroring test step.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_erroring_test_step_for_asc.xml', asc_config_file, asc_global_props)
    zz_runner.add_test_case('passed', test_steps=[{'state': 'error'}])

    return zz_runner


# noinspection PyShadowingNames
@pytest.fixture(scope='module')
def mixed_status_test_steps_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with 4 test steps covering the various test execution
     states in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    test_steps = [{'state': 'passed'},
                  {'state': 'failure'},
                  {'state': 'skipped'}]

    zz_runner = _zigzag_runner_factory('mixed_status_test_steps_for_asc.xml', asc_config_file, asc_global_props)
    zz_runner.add_test_case('failure', test_steps=test_steps)

    return zz_runner


# noinspection PyShadowingNames
@pytest.fixture(scope='module')
def single_skipping_test_step_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "mk8s" CI environment with a test case containing one skipping test step.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_skipping_test_step_for_mk8s.xml', mk8s_config_file, mk8s_global_props)
    zz_runner.add_test_case('passed', test_steps=[{'state': 'skipped'}])

    return zz_runner


# noinspection PyShadowingNames
@pytest.fixture(scope='module')
def single_erroring_test_step_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "mk8s" CI environment with a test case containing one erroring test step.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_erroring_test_step_for_mk8s.xml', mk8s_config_file, mk8s_global_props)
    zz_runner.add_test_case('passed', test_steps=[{'state': 'error'}])

    return zz_runner


# noinspection PyShadowingNames
@pytest.fixture(scope='module')
def mixed_status_test_steps_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with 4 test steps covering the various test execution
     states in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    test_steps = [{'state': 'passed'},
                  {'state': 'failure'},
                  {'state': 'skipped'}]

    zz_runner = _zigzag_runner_factory('mixed_status_test_steps_for_mk8s.xml', mk8s_config_file, mk8s_global_props)
    zz_runner.add_test_case('failure', test_steps=test_steps)

    return zz_runner


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestSteps(object):
    """Test cases for basic functionality for test cases with steps."""

    # noinspection PyUnresolvedReferences
    def test_single_passing_test_step_for_asc(self, single_passing_test_step_for_asc):
        """Verify ZigZag can publish results from the "asc" CI environment with one passing test step in the JUnitXML
        file.
        """

        # Setup
        single_passing_test_step_for_asc.assert_invoke_zigzag()
        test_runs = single_passing_test_step_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_run_status_exp = 'Passed'

        # Test
        assert len(test_runs) == 1
        assert len(single_passing_test_step_for_asc.tests) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_single_skipping_test_step_for_asc(self, single_skipping_test_step_for_asc):
        """Verify ZigZag can publish results from the "asc" CI environment with one skipping test step in the JUnitXML
        file.
        """

        # Setup
        single_skipping_test_step_for_asc.assert_invoke_zigzag()
        test_runs = single_skipping_test_step_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_run_status_exp = 'Incomplete'

        # Test
        assert len(test_runs) == 1
        assert len(single_skipping_test_step_for_asc.tests) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_single_erroring_test_step_for_asc(self, single_erroring_test_step_for_asc):
        """Verify ZigZag can publish results from the "asc" CI environment with one erroring test step in the JUnitXML
        file.
        """

        # Setup
        single_erroring_test_step_for_asc.assert_invoke_zigzag()
        test_runs = single_erroring_test_step_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_run_status_exp = 'Failed'
        test_failure_msg_regex_exp = r'Test execution state: error'

        # Test
        assert len(test_runs) == 1
        assert len(single_erroring_test_step_for_asc.tests) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)

    # noinspection PyUnresolvedReferences
    def test_mixed_status_test_steps_for_asc(self, mixed_status_test_steps_for_asc):
        """Verify ZigZag can publish results from the "asc" CI environment with multiple test steps in the JUnitXML
        file.
        """

        # Setup
        mixed_status_test_steps_for_asc.assert_invoke_zigzag()
        test_runs = mixed_status_test_steps_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_run_status_exp = 'Failed'
        test_failure_msg_regex_exp = r'Test execution state: failure'

        # Test
        assert len(test_runs) == 1
        assert len(mixed_status_test_steps_for_asc.tests) == 3
        pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)

    # noinspection PyUnresolvedReferences
    def test_single_passing_test_step_for_mk8s(self, single_passing_test_step_for_mk8s):
        """Verify ZigZag can publish results from the "mk8s" CI environment with one passing test step in the JUnitXML
        file.
        """

        # Setup
        single_passing_test_step_for_mk8s.assert_invoke_zigzag()
        test_runs = single_passing_test_step_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_run_status_exp = 'Passed'

        # Test
        assert len(test_runs) == 1
        assert len(single_passing_test_step_for_mk8s.tests) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_single_skipping_test_step_for_mk8s(self, single_skipping_test_step_for_mk8s):
        """Verify ZigZag can publish results from the "mk8s" CI environment with one skipping test step in the JUnitXML
        file.
        """

        # Setup
        single_skipping_test_step_for_mk8s.assert_invoke_zigzag()
        test_runs = single_skipping_test_step_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_run_status_exp = 'Incomplete'

        # Test
        assert len(test_runs) == 1
        assert len(single_skipping_test_step_for_mk8s.tests) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_single_erroring_test_step_for_mk8s(self, single_erroring_test_step_for_mk8s):
        """Verify ZigZag can publish results from the "asc" CI environment with one erroring test step in the JUnitXML
        file.
        """

        # Setup
        single_erroring_test_step_for_mk8s.assert_invoke_zigzag()
        test_runs = single_erroring_test_step_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_run_status_exp = 'Failed'
        test_failure_msg_regex_exp = r'Test execution state: error'

        # Test
        assert len(test_runs) == 1
        assert len(single_erroring_test_step_for_mk8s.tests) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)

    # noinspection PyUnresolvedReferences
    def test_mixed_status_test_steps_for_mk8s(self, mixed_status_test_steps_for_mk8s):
        """Verify ZigZag can publish results from the "asc" CI environment with multiple test steps in the JUnitXML
        file.
        """

        # Setup
        mixed_status_test_steps_for_mk8s.assert_invoke_zigzag()
        test_runs = mixed_status_test_steps_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_run_status_exp = 'Failed'
        test_failure_msg_regex_exp = r'Test execution state: failure'

        # Test
        assert len(test_runs) == 1
        assert len(mixed_status_test_steps_for_mk8s.tests) == 3
        pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)
