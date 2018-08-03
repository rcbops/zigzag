# -*- coding: utf-8 -*-

"""Tests for verifying requirement linking."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestRequirementLinking(object):
    """Test cases for validating that test cases in qTest can be linked with requirements based on Jira tickets."""

    def test_requirement_link_for_asc(self, mixed_status_tests_for_asc):
        """Verify the qTest test cases can be linked to requirements using the "asc" CI environment."""

        # Setup
        mixed_status_tests_for_asc.tests.assert_requirements_exist()

        # Test
        mixed_status_tests_for_asc.assert_invoke_zigzag()

        # Re-run ZigZag because requirement linking is eventually consistent and a second run guarantees ZigZag will
        # link all the test cases.
        mixed_status_tests_for_asc.assert_invoke_zigzag(force_clean_up=False)

        mixed_status_tests_for_asc.tests.assert_requirements_linked()

    def test_missing_link_for_asc(self, single_passing_test_for_asc):
        """Verify that links will not be created for requirements that don't exist using the "asc" CI environment."""

        # Setup
        single_passing_test_for_asc.tests.clean_up_requirements()

        # Test
        single_passing_test_for_asc.assert_invoke_zigzag()

        # Re-run ZigZag because requirement linking is eventually consistent and a second run guarantees ZigZag will
        # link all the test cases.
        single_passing_test_for_asc.assert_invoke_zigzag(force_clean_up=False)

        with pytest.raises(AssertionError):
            single_passing_test_for_asc.tests.assert_requirements_linked()

    def test_requirement_link_for_mk8s(self, mixed_status_tests_for_mk8s):
        """Verify the qTest test cases can be linked to requirements using the "mk8s" CI environment."""

        # Setup
        mixed_status_tests_for_mk8s.tests.assert_requirements_exist()

        # Test
        mixed_status_tests_for_mk8s.assert_invoke_zigzag()

        # Re-run ZigZag because requirement linking is eventually consistent and a second run guarantees ZigZag will
        # link all the test cases.
        mixed_status_tests_for_mk8s.assert_invoke_zigzag(force_clean_up=False)

        mixed_status_tests_for_mk8s.tests.assert_requirements_linked()

    def test_missing_link_for_mk8s(self, single_passing_test_for_mk8s):
        """Verify that links will not be created for requirements that don't exist using the "mk8s" CI environment."""

        # Setup
        single_passing_test_for_mk8s.tests.clean_up_requirements()

        # Test
        single_passing_test_for_mk8s.assert_invoke_zigzag()

        # Re-run ZigZag because requirement linking is eventually consistent and a second run guarantees ZigZag will
        # link all the test cases.
        single_passing_test_for_mk8s.assert_invoke_zigzag(force_clean_up=False)

        with pytest.raises(AssertionError):
            single_passing_test_for_mk8s.tests.assert_requirements_linked()
