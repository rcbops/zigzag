# -*- coding: utf-8 -*-

"""Basic functionality tests for proving that ZigZag can publish results to qTest accurately."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestPassing(object):
    """Test cases for tests with 'Passed' status in qTest."""

    # noinspection PyUnresolvedReferences
    def test_publish_asc_single_passing(self, single_passing_test_for_asc):
        """Verify ZigZag can publish results from the "asc" CI environment with one passing test in the JUnitXML
        file.
        """

        # Setup
        single_passing_test_for_asc.assert_invoke_zigzag()
        test_runs = single_passing_test_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_run_status_exp = 'Passed'

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_publish_mk8s_single_passing(self, single_passing_test_for_mk8s):
        """Verify ZigZag can publish results from the "mk8s" CI environment with one passing test in the JUnitXML
        file.
        """

        # Setup
        single_passing_test_for_mk8s.assert_invoke_zigzag()
        test_runs = single_passing_test_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_run_status_exp = 'Passed'

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_publish_asc_multiple_passing(self, multiple_passing_tests_for_asc):
        """Verify ZigZag can publish results from the "asc" CI environment with multiple passing tests in the
        JUnitXML file.
        """

        # Setup
        multiple_passing_tests_for_asc.assert_invoke_zigzag()

        # Expectations
        test_run_status_exp = 'Passed'

        # Test
        for test in multiple_passing_tests_for_asc.tests:
            test_runs = test.qtest_test_runs
            assert len(test_runs) == 1
            pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_publish_mk8s_multiple_passing(self, multiple_passing_tests_for_mk8s):
        """Verify ZigZag can publish results from the "mk8s" CI environment with multiple passing tests in the
        JUnitXML file.
        """

        # Setup
        multiple_passing_tests_for_mk8s.assert_invoke_zigzag()

        # Expectations
        test_run_status_exp = 'Passed'

        # Test
        for test in multiple_passing_tests_for_mk8s.tests:
            test_runs = test.qtest_test_runs
            assert len(test_runs) == 1
            pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)


class TestFailing(object):
    """Test cases for tests with 'Failed' status in qTest."""

    # noinspection PyUnresolvedReferences
    def test_publish_asc_multiple_failing(self, multiple_failing_tests_for_asc):
        """Verify ZigZag can publish results from the "asc" CI environment with multiple failing tests in the
        JUnitXML file.
        """

        # Setup
        multiple_failing_tests_for_asc.assert_invoke_zigzag()

        # Expectations
        test_run_status_exp = 'Failed'

        # Test
        for test in multiple_failing_tests_for_asc.tests:
            test_runs = test.qtest_test_runs
            assert len(test_runs) == 1
            pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_publish_mk8s_multiple_failing(self, multiple_failing_tests_for_mk8s):
        """Verify ZigZag can publish results from the "mk8s" CI environment with multiple failing tests in the
        JUnitXML file.
        """

        # Setup
        multiple_failing_tests_for_mk8s.assert_invoke_zigzag()

        # Expectations
        test_run_status_exp = 'Failed'

        # Test
        for test in multiple_failing_tests_for_mk8s.tests:
            test_runs = test.qtest_test_runs
            assert len(test_runs) == 1
            pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)


class TestErroring(object):
    """Test cases for tests with 'Errored' status in qTest."""

    # noinspection PyUnresolvedReferences
    def test_publish_asc_multiple_erroring(self, multiple_erroring_tests_for_asc):
        """Verify ZigZag can publish results from the "asc" CI environment with multiple erroring tests in the
        JUnitXML file.
        """

        # Setup
        multiple_erroring_tests_for_asc.assert_invoke_zigzag()

        # Expectations
        test_run_status_exp = 'Failed'

        # Test
        for test in multiple_erroring_tests_for_asc.tests:
            test_runs = test.qtest_test_runs
            assert len(test_runs) == 1
            pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_publish_mk8s_multiple_erroring(self, multiple_erroring_tests_for_mk8s):
        """Verify ZigZag can publish results from the "mk8s" CI environment with multiple erroring tests in the
        JUnitXML file.
        """

        # Setup
        multiple_erroring_tests_for_mk8s.assert_invoke_zigzag()

        # Expectations
        test_run_status_exp = 'Failed'

        # Test
        for test in multiple_erroring_tests_for_mk8s.tests:
            test_runs = test.qtest_test_runs
            assert len(test_runs) == 1
            pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)


class TestSkipping(object):
    """Test cases for tests with 'Incomplete' status in qTest."""

    # noinspection PyUnresolvedReferences
    def test_publish_asc_multiple_skipping(self, multiple_skipping_tests_for_asc):
        """Verify ZigZag can publish results from the "asc" CI environment with multiple skipping tests in the
        JUnitXML file.
        """

        # Setup
        multiple_skipping_tests_for_asc.assert_invoke_zigzag()

        # Expectations
        test_run_status_exp = 'Incomplete'

        # Test
        for test in multiple_skipping_tests_for_asc.tests:
            test_runs = test.qtest_test_runs
            assert len(test_runs) == 1
            pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_publish_mk8s_multiple_skipping(self, multiple_skipping_tests_for_mk8s):
        """Verify ZigZag can publish results from the "mk8s" CI environment with multiple skipping tests in the
        JUnitXML file.
        """

        # Setup
        multiple_skipping_tests_for_mk8s.assert_invoke_zigzag()

        # Expectations
        test_run_status_exp = 'Incomplete'

        # Test
        for test in multiple_skipping_tests_for_mk8s.tests:
            test_runs = test.qtest_test_runs
            assert len(test_runs) == 1
            pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)


class TestMixed(object):
    """Test cases for test suites with 'Passed', 'Failed' and 'Incomplete' test statuses in qTest."""

    # noinspection PyUnresolvedReferences
    def test_publish_asc_mixed_status(self, mixed_status_tests_for_asc):
        """Verify ZigZag can publish results from the "asc" CI environment with multiple skipping tests in the
        JUnitXML file.
        """

        # Setup
        mixed_status_tests_for_asc.assert_invoke_zigzag()

        # Expectations
        test_run_status_exps = ['Passed', 'Failed', 'Failed', 'Incomplete']

        # Test
        for test, test_run_status_exp in zip(mixed_status_tests_for_asc.tests, test_run_status_exps):
            test_runs = test.qtest_test_runs
            assert len(test_runs) == 1
            pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)

    # noinspection PyUnresolvedReferences
    def test_publish_mk8s_mixed_status(self, mixed_status_tests_for_mk8s):
        """Verify ZigZag can publish results from the "mk8s" CI environment with multiple skipping tests in the
        JUnitXML file.
        """

        # Setup
        mixed_status_tests_for_mk8s.assert_invoke_zigzag()

        # Expectations
        test_run_status_exps = ['Passed', 'Failed', 'Failed', 'Incomplete']

        # Test
        for test, test_run_status_exp in zip(mixed_status_tests_for_mk8s.tests, test_run_status_exps):
            test_runs = test.qtest_test_runs
            assert len(test_runs) == 1
            pytest.helpers.assert_qtest_property(test_runs[0], 'Status', test_run_status_exp)
