# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import re


class ModuleHierarchyFacade(object):
    def __init__(self, classname, mediator):
        """Create a ModuleHierarchyFacade

        Args:
            classname (str): A string representing the 'classname' attribute on the 'testcase' XML element.
            mediator (ZigZag): the mediator that stores shared data
        """

        self._mediator = mediator
        self._classname = classname

    def get_module_hierarchy(self):
        """Get module hierarchy

        Returns:
            list[str]: The strings to use for the module_hierarchy
        """

        if self._mediator.ci_environment == 'asc':
            return self._asc()
        elif self._mediator.ci_environment == 'mk8s':
            return self._mk8s()
        else:
            return self._asc()  # This is the default

    def _asc(self):
        """Gets the module hierarchy for asc test cases

        Returns:
            list[str]: The strings to use for the module_hierarchy
        """

        testsuite_props = self._mediator.testsuite_props
        self._set_test_cycle(testsuite_props['RPC_PRODUCT_RELEASE'])
        module_hierarchy = [testsuite_props['RPC_RELEASE'],             # RPC Release Version (e.g. 16.0.0)
                            testsuite_props['JOB_NAME'],                # CI Job name (e.g. PM_rpc-openstack-pike-xenial_mnaio_no_artifacts-swift-system) # noqa
                            testsuite_props['MOLECULE_TEST_REPO'],      # (e.g. molecule-validate-neutron-deploy)
                            testsuite_props['MOLECULE_SCENARIO_NAME']]  # (e.g. "default")

        try:
            testcase_groups = self._mediator.utility_facade.testcase_group_rgx.search(self._classname).groups()
        except AttributeError:
            raise RuntimeError("Test case '{}' has an invalid 'classname' attribute!".format(self._classname))

        module_hierarchy.append(testcase_groups[0])         # Always append at least the filename of the test grouping.
        if testcase_groups[1]:
            module_hierarchy.append(testcase_groups[1])     # Append the class name of tests if specified.

        return module_hierarchy

    def _mk8s(self):
        """Gets the module hierarchy for test cases that are mk8s

        Returns:
            list[str]: The strings to use for the module_hierarchy
        """

        pr_regex = re.compile(".*(PR-\d+).*")
        pr = re.match(pr_regex, self._mediator.testsuite_props['GIT_BRANCH'])

        if pr:
            self._set_test_cycle('PR')
            # organize all PR related testing by pr number ex: 'PR-123'
            module_hierarchy = [pr.group(1), self._classname]  # The specific PR
        else:
            # organize all non PR related testing by branch name
            self._set_test_cycle(self._mediator.testsuite_props['BRANCH_NAME'])
            module_hierarchy = [self._classname]

        return module_hierarchy

    def _set_test_cycle(self, cycle):
        """Sets the test cycle if it has not already been defined"""

        if self._mediator.qtest_test_cycle is None:
            self._mediator.qtest_test_cycle = cycle
