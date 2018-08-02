# -*- coding: utf-8 -*-

"""Tests for verifying failure output."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestFailureOutputField(object):
    """Test cases for validating that failing/erroring test cases will have failure messages populated in the qTest
    'Failure Output' test log field.
    """

    # noinspection PyUnresolvedReferences
    def test_failure_output_for_asc(self, single_failing_test_for_asc):
        """Verify the qTest 'Failure Output' test log field is populated with the correct message for a single test
        failing from the "asc" CI environment.
        """

        # Setup
        single_failing_test_for_asc.assert_invoke_zigzag()
        test_runs = single_failing_test_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_regex_exp = r'Test execution state: failure \(long\)'

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)

    # noinspection PyUnresolvedReferences
    def test_failure_output_after_state_change_for_asc(self, single_failing_test_for_asc):
        """Verify the qTest 'Failure Output' test log field is populated with the correct message for a single test
        failing from the "asc" CI environment.
        """

        # Setup
        single_failing_test_for_asc.assert_invoke_zigzag()
        test_runs = single_failing_test_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_regex_exp = r'Test execution state: failure \(long\)'

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)

        # Setup
        single_failing_test_for_asc.tests[0].state = 'passed'   # Change the state of the test to 'passed'
        single_failing_test_for_asc.invoke_zigzag(force_clean_up=False)     # Re-run ZigZag
        test_runs = single_failing_test_for_asc.tests[0].qtest_test_runs

        # Test
        single_failing_test_for_asc.assert_queue_job_complete()
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Output', '')

    # noinspection PyUnresolvedReferences
    def test_failure_output_for_mk8s(self, single_failing_test_for_mk8s):
        """Verify the qTest 'Failure Output' test log field is populated with the correct message for a single test
        failing from the "mk8s" CI environment.
        """

        # Setup
        single_failing_test_for_mk8s.assert_invoke_zigzag()
        test_runs = single_failing_test_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_regex_exp = r'Test execution state: failure \(long\)'

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)

    # noinspection PyUnresolvedReferences
    def test_failure_output_after_state_change_for_mk8s(self, single_failing_test_for_mk8s):
        """Verify the qTest 'Failure Output' test log field is populated with the correct message for a single test
        failing from the "mk8s" CI environment.
        """

        # Setup
        single_failing_test_for_mk8s.assert_invoke_zigzag()
        test_runs = single_failing_test_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_regex_exp = r'Test execution state: failure \(long\)'

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)

        # Setup
        single_failing_test_for_mk8s.tests[0].state = 'passed'  # Change the state of the test to 'passed'
        single_failing_test_for_mk8s.invoke_zigzag(force_clean_up=False)  # Re-run ZigZag
        test_runs = single_failing_test_for_mk8s.tests[0].qtest_test_runs

        # Test
        single_failing_test_for_mk8s.assert_queue_job_complete()
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Output', '')
