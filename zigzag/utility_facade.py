# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import re
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

        self._testcase_group_rgx = re.compile(r'tests\.(test_[\w-]+)\.?(Test\w+)?$')

    @property
    def testcase_group_rgx(self):
        """A compiled regular expression for extracting the test module and class. (Only grabs the class if the user
        made a test suite using a Python class)

        Returns:
            re.RegexObject
        """

        return self._testcase_group_rgx

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
