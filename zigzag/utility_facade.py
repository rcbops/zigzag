# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import swagger_client
from swagger_client.rest import ApiException


class UtilityFacade(object):

    def __init__(self, mediator):
        """A facade to contain utilities
        utilities contained in this facade should be reusable between facades

        Args:
            mediator (ZigZag): the mediator that stores shared data
        """
        self._mediator = mediator
        self._field_api = swagger_client.FieldApi()

    def find_custom_field_id_by_label(self, field_name, object_type):
        """Find a custom field id by its label

        Args:
            field_name (str): The name of the custom field
            object_type (str): The object type to search for the custom field on

        Returns:
            int: the id of the field that has the matching label

        Raises:
            RuntimeError: The qTest API reported an error!
        """

        try:
            for field in self._field_api.get_fields(self._mediator.qtest_project_id, object_type):
                if field.label == field_name:
                    return field.id
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))

    def discover_parent_test_cycle(self, test_cycle_name):  # consider moving this to module hierarchy facade in future
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
