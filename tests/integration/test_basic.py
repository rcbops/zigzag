# -*- coding: utf-8 -*-

"""Basic functionality tests for proving that ZigZag can publish results to qTest accurately."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import uuid
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


class TestRename(object):
    """Validate that test cases can be renamed."""

    # noinspection PyUnresolvedReferences
    def test_rename_test_case_for_asc(self, single_passing_test_for_asc):
        """Verify that renaming a test case (keeping the same 'test_id') preserves the original test case name, but
        the associated test run uses the updated name for the "asc" CI environment.
        """

        # Setup
        single_passing_test_for_asc.assert_invoke_zigzag()

        # Expectations
        original_test_case_name_exp = single_passing_test_for_asc.tests[0].name
        new_test_case_name_exp = "test_rename_{}".format(str(uuid.uuid1()))

        # Test
        single_passing_test_for_asc.tests[0].name = new_test_case_name_exp
        single_passing_test_for_asc.assert_invoke_zigzag(force_clean_up=False)

        pytest.helpers.assert_qtest_property(single_passing_test_for_asc.tests[0].qtest_test_case_info,
                                             'name',
                                             original_test_case_name_exp)

        pytest.helpers.assert_qtest_property(single_passing_test_for_asc.tests[0].qtest_test_runs[0],
                                             'name',
                                             new_test_case_name_exp)

    # noinspection PyUnresolvedReferences
    def test_rename_test_case_for_mk8s(self, single_passing_test_for_mk8s):
        """Verify that renaming a test case (keeping the same 'test_id') preserves the original test case name, but
        the associated test run uses the updated name for the "mk8s" CI environment.
        """

        # Setup
        single_passing_test_for_mk8s.assert_invoke_zigzag()

        # Expectations
        original_test_case_name_exp = single_passing_test_for_mk8s.tests[0].name
        new_test_case_name_exp = "test_rename_{}".format(str(uuid.uuid1()))

        # Test
        single_passing_test_for_mk8s.tests[0].name = new_test_case_name_exp
        single_passing_test_for_mk8s.assert_invoke_zigzag(force_clean_up=False)

        pytest.helpers.assert_qtest_property(single_passing_test_for_mk8s.tests[0].qtest_test_case_info,
                                             'name',
                                             original_test_case_name_exp)

        pytest.helpers.assert_qtest_property(single_passing_test_for_mk8s.tests[0].qtest_test_runs[0],
                                             'name',
                                             new_test_case_name_exp)

    # noinspection PyUnresolvedReferences
    def test_move_test_case_to_suite_for_asc(self, single_passing_test_for_asc):
        """Verify that moving a test case to a test suite (keeping the same 'test_id') will show execution results under
        the old test cycle and under a new test cycle named after the suite for the "asc" CI environment.
        """

        # Setup
        single_passing_test_for_asc.tests[0].class_name = 'tests.test_default'  # Enforce known starting point.
        single_passing_test_for_asc.assert_invoke_zigzag()
        original_parent_test_cycle = single_passing_test_for_asc.tests[0].qtest_parent_test_cycles[0].name

        # Expectations
        new_parent_test_cycle_name_exp = 'TestSuite'

        # Test
        single_passing_test_for_asc.tests[0].class_name = "tests.test_default.{}".format(new_parent_test_cycle_name_exp)
        single_passing_test_for_asc.assert_invoke_zigzag(force_clean_up=False)
        parent_test_cycles = single_passing_test_for_asc.tests[0].qtest_parent_test_cycles

        # The qTest API returns test associated test runs from newest to oldest.
        pytest.helpers.assert_qtest_property(parent_test_cycles[0],
                                             'name',
                                             new_parent_test_cycle_name_exp)

        pytest.helpers.assert_qtest_property(parent_test_cycles[1],
                                             'name',
                                             original_parent_test_cycle)

    # noinspection PyUnresolvedReferences
    def test_move_test_case_to_suite_for_mk8s(self, single_passing_test_for_mk8s):
        """Verify that moving a test case to a test suite (keeping the same 'test_id') will show execution results under
        the old test cycle and under a new test cycle named after the suite for the "asc" CI environment.
        """

        # Setup
        single_passing_test_for_mk8s.tests[0].class_name = 'tests.test_default'  # Enforce known starting point.
        single_passing_test_for_mk8s.assert_invoke_zigzag()
        original_parent_test_cycle = single_passing_test_for_mk8s.tests[0].qtest_parent_test_cycles[0].name

        # Expectations
        new_parent_test_cycle_name_exp = 'tests.test_default.TestSuite'

        # Test
        single_passing_test_for_mk8s.tests[0].class_name = new_parent_test_cycle_name_exp
        single_passing_test_for_mk8s.assert_invoke_zigzag(force_clean_up=False)
        parent_test_cycles = single_passing_test_for_mk8s.tests[0].qtest_parent_test_cycles

        # The qTest API returns test associated test runs from newest to oldest.
        pytest.helpers.assert_qtest_property(parent_test_cycles[0],
                                             'name',
                                             new_parent_test_cycle_name_exp)

        pytest.helpers.assert_qtest_property(parent_test_cycles[1],
                                             'name',
                                             original_parent_test_cycle)

    # noinspection PyUnresolvedReferences
    def test_move_test_case_to_different_file_for_asc(self, single_passing_test_for_asc):
        """Verify that moving a test case to a test suite (keeping the same 'test_id') will show execution results under
        the old test cycle and under a new test cycle named after the the file name for the "mk8s" CI environment.
        """

        # Setup
        single_passing_test_for_asc.tests[0].class_name = 'tests.test_default'  # Enforce known starting point.
        single_passing_test_for_asc.tests[0].file_path = 'tests/test_default.py'  # Enforce known starting point.
        single_passing_test_for_asc.assert_invoke_zigzag()
        original_parent_test_cycle = single_passing_test_for_asc.tests[0].qtest_parent_test_cycles[0].name

        # Expectations
        new_parent_test_cycle_name_exp = 'test_fancy'

        # Test
        single_passing_test_for_asc.tests[0].class_name = "tests.{}".format(new_parent_test_cycle_name_exp)
        single_passing_test_for_asc.tests[0].file_path = "tests/{}.py".format(new_parent_test_cycle_name_exp)
        single_passing_test_for_asc.assert_invoke_zigzag(force_clean_up=False)
        parent_test_cycles = single_passing_test_for_asc.tests[0].qtest_parent_test_cycles

        # The qTest API returns test associated test runs from newest to oldest.
        pytest.helpers.assert_qtest_property(parent_test_cycles[0],
                                             'name',
                                             new_parent_test_cycle_name_exp)

        pytest.helpers.assert_qtest_property(parent_test_cycles[1],
                                             'name',
                                             original_parent_test_cycle)

    # noinspection PyUnresolvedReferences
    def test_move_test_case_to_different_file_for_mk8s(self, single_passing_test_for_mk8s):
        """Verify that moving a test case to a test suite (keeping the same 'test_id') will show execution results under
        the old test cycle and under a new test cycle named after the the file name for the "mk8s" CI environment.
        """

        # Setup
        single_passing_test_for_mk8s.tests[0].class_name = 'tests.test_default'  # Enforce known starting point.
        single_passing_test_for_mk8s.tests[0].file_path = 'tests/test_default.py'  # Enforce known starting point.
        single_passing_test_for_mk8s.assert_invoke_zigzag()
        original_parent_test_cycle = single_passing_test_for_mk8s.tests[0].qtest_parent_test_cycles[0].name

        # Expectations
        new_parent_test_cycle_name_exp = 'tests.test_fancy'

        # Test
        single_passing_test_for_mk8s.tests[0].class_name = new_parent_test_cycle_name_exp
        single_passing_test_for_mk8s.tests[0].file_path = 'tests/test_fancy.py'
        single_passing_test_for_mk8s.assert_invoke_zigzag(force_clean_up=False)
        parent_test_cycles = single_passing_test_for_mk8s.tests[0].qtest_parent_test_cycles

        # The qTest API returns test associated test runs from newest to oldest.
        pytest.helpers.assert_qtest_property(parent_test_cycles[0],
                                             'name',
                                             new_parent_test_cycle_name_exp)

        pytest.helpers.assert_qtest_property(parent_test_cycles[1],
                                             'name',
                                             original_parent_test_cycle)
