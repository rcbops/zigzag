# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import re
import swagger_client
from swagger_client.rest import ApiException


class ModuleHierarchyFacade(object):
    """A class to contain logic that calculates ModuleHierarchy & test_cycle"""
    def __init__(self, mediator):
        """Create a ModuleHierarchyFacade

        Args:
            mediator (ZigZag): the mediator that stores shared data
        """

        self._mediator = mediator
        self._pr_regex = re.compile(r'.*(PR-\d+).*')
        self._pr_match = None

    def get_module_hierarchy(self, classname):
        """Get module hierarchy

        Args:
            classname (str): A string representing the 'classname' attribute on the 'testcase' XML element.

        Returns:
            list[str]: The strings to use for the module_hierarchy
        """

        if self._mediator.ci_environment == 'asc':
            return self._asc(classname)
        elif self._mediator.ci_environment == 'mk8s':
            return self._mk8s(classname)
        elif self._mediator.test_runner == 'tempest':
            return self._tempest(classname)
        else:
            return self._asc(classname)  # This is the default

    def get_test_cycle_name(self):
        """Gets the test_cycle name

        Returns:
            str: The test_cycle name
        """
        if self._mediator.ci_environment == 'asc':
            return self._mediator.testsuite_props['RPC_PRODUCT_RELEASE']
        elif self._mediator.ci_environment == 'mk8s':
            # organize all PR related testing by pr number ex: 'PR-123'
            # organize all non PR related testing by branch name
            return 'PR' if self.pr_match else self._mediator.testsuite_props['BRANCH_NAME']
        elif self._mediator.test_runner == 'tempest':
            return 'Tempest'
        else:
            return self._mediator.testsuite_props['RPC_PRODUCT_RELEASE']

    def discover_root_test_cycle(self, test_cycle_name):
        """Search for a test cycle at the root of the qTest Test Execution with a matching name. (Case insensitive) If a
        matching test cycle name is not found then a test cycle will be created with the given name.

        Args:
            test_cycle_name (str): The test cycle name (e.g. queens) to search for in an case insensitive fashion.

        Returns:
            str: A qTest test cycle PID. (e.g. CL-123)

        Raises:
            RuntimeError: Failed to retrieve/create qTest test cycle(s).
        """

        auto_api = swagger_client.TestcycleApi()
        project_id = self._mediator.qtest_project_id
        test_cycle_pid = None

        try:
            test_cycles = {tc.to_dict()['name']: tc.to_dict()['pid'] for tc in auto_api.get_test_cycles(project_id)}

            if test_cycle_name.lower() not in [tcn.lower() for tcn in test_cycles.keys()]:
                test_cycle_pid = auto_api.create_cycle(
                    project_id=project_id,
                    parent_id=0,
                    parent_type='root',
                    body=swagger_client.TestCycleResource(
                        name=test_cycle_name)).to_dict()['pid']
            else:
                try:
                    test_cycle_pid = test_cycles[test_cycle_name]
                except KeyError:
                    for key in list(test_cycles.keys()):
                        if key.lower() == test_cycle_name.lower():
                            # this will take the last match found
                            # once we can warn we should warn the user that we found duplicate cycles
                            test_cycle_pid = test_cycles[key]
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))

        return test_cycle_pid

    @property
    def pr_match(self):
        """Tells if tests results are from a PR

        Returns:
            match: the regex match object
        """
        if self._pr_match is None:
            self._pr_match = re.match(self._pr_regex, self._mediator.testsuite_props['BRANCH_NAME'])

        return self._pr_match

    def _asc(self, classname):
        """Gets the module hierarchy for asc test cases

        Args:
            classname (str): A string representing the 'classname' attribute on the 'testcase' XML element.

        Returns:
            list[str]: The strings to use for the module_hierarchy
        """

        testsuite_props = self._mediator.testsuite_props
        module_hierarchy = [testsuite_props['RPC_RELEASE'],             # RPC Release Version (e.g. 16.0.0)
                            testsuite_props['JOB_NAME'],                # CI Job name (e.g. PM_rpc-openstack-pike-xenial_mnaio_no_artifacts-swift-system) # noqa
                            testsuite_props['MOLECULE_TEST_REPO'],      # (e.g. molecule-validate-neutron-deploy)
                            testsuite_props['MOLECULE_SCENARIO_NAME']]  # (e.g. "default")

        try:
            testcase_groups = self._mediator.utility_facade.testcase_group_rgx.search(classname).groups()
        except AttributeError:
            raise RuntimeError("Test case '{}' has an invalid 'classname' attribute!".format(classname))

        module_hierarchy.append(testcase_groups[0])         # Always append at least the filename of the test grouping.
        if testcase_groups[1]:
            module_hierarchy.append(testcase_groups[1])     # Append the class name of tests if specified.

        return module_hierarchy

    def _mk8s(self, classname):
        """Gets the module hierarchy for test cases that are mk8s

        Args:
            classname (str): A string representing the 'classname' attribute on the 'testcase' XML element.

        Returns:
            list[str]: The strings to use for the module_hierarchy
        """

        if self.pr_match:
            module_hierarchy = [self.pr_match.group(1), classname]  # The specific PR
        else:
            module_hierarchy = [classname]

        return module_hierarchy

    def _tempest(self, classname):
        """Gets the module hierarchy for tempest test cases

        Returns:
            list[str]: The strings to use for the module_hierarchy
        """
        return [classname]  # this is a placeholder, use something more meaningful
