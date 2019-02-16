# -*- coding: utf-8 -*-

"""Test supported configurations of zigzag."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import uuid
import pytest


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestConfig(object):
    # noinspection PyUnresolvedReferences
    def test_publish_single_passing_custom_mod_hierarchy(self, single_passing_test_with_custom_mod_hierarchy):
        """Verify ZigZag can publish results from the "asc" CI environment with one passing test in the JUnitXML
        file.
        """

        # Setup
        single_passing_test_with_custom_mod_hierarchy.assert_invoke_zigzag()
        test_runs = single_passing_test_with_custom_mod_hierarchy.tests[0].qtest_test_runs

        # Expectations
        parent_test_cycle_name_exp = 'node2'

        test = single_passing_test_with_custom_mod_hierarchy.tests[0]
        qtest_parent_test_cycle_name = test.qtest_parent_test_cycles[0].name

        # Test
        assert(parent_test_cycle_name_exp == qtest_parent_test_cycle_name)
