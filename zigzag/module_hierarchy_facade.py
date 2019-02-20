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

    def get_module_hierarchy(self, classname):
        """Get module hierarchy

        Args:
            classname (str): A string representing the 'classname' attribute on the 'testcase' XML element.

        Returns:
            list[str]: The strings to use for the module_hierarchy
        """

        modhierarchy = []
        defined_hierarchy = self._mediator.config_dict.get_config('module_hierarchy')
        test_file_name = classname[classname.rfind(".")+1:]
        try:
            re.search("(^[a-zA-Z_][a-zA-Z0-9_]*$)", test_file_name).groups()
            modhierarchy = [str(h) for h in defined_hierarchy]
            modhierarchy.append(test_file_name)
        except AttributeError:
            raise RuntimeError("Test case '{}' has an invalid 'classname' attribute!".format(classname))
        return modhierarchy

    def get_test_cycle_name(self):
        """Gets the test_cycle name

        Returns:
            str: The test_cycle name
        """
        return self._mediator.config_dict.get_config('test_cycle')

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
