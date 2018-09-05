# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import swagger_client
from random import choice
from swagger_client.rest import ApiException


# ======================================================================================================================
# Classes
# ======================================================================================================================
class JiraRequirementInfo(object):
    # Class variables
    _jira_req_id_cache = {}     # { str(<JIRA-ID>): int(<qTest Resource ID>) }

    def __init__(self,
                 qtest_api_token,
                 qtest_project_id,
                 qtest_req_module_id,
                 jira_id=None):
        """Create a qTest requirement that represent a Jira tickets Provide methods for validating state and
        association with qTest test cases.

        Args:
            qtest_api_token (str): The API token for the target qTest project.
            qtest_project_id (int): The target qTest project under test.
            qtest_req_module_id (int): The module to use as the parent for this requirement in the qTest
                'Requirements' view.
            jira_id (str): The state of the test. (Automatically generated if value is None)

        Raises:
            RuntimeError: Invalid value provided for the 'state' argument.
        """

        self._qtest_api_token = qtest_api_token
        self._qtest_project_id = qtest_project_id
        self._qtest_req_module_id = qtest_req_module_id
        self._jira_id = jira_id if jira_id else "JIRA-{}".format(choice(range(1, 100000)))
        self._name = "{} {}".format(self._jira_id, 'Requirement')

        self._qtest_req_id = None

    @property
    def name(self):
        """The name of the requirement. (Jira ID + 'Requirement')

        Returns:
            str
        """

        return self._name

    @property
    def jira_id(self):
        """The Jira ID associated with this requirement.

        Returns:
            str
        """

        return self._jira_id

    @property
    def qtest_req_id(self):
        """The qTest requirement ID for the given requirement.

        Returns:
            int

        Raises:
            AssertionError: Test case does not exist.
        """

        if not self._qtest_req_id:
            self.assert_exists()

        return self._qtest_req_id

    @property
    def qtest_req_info(self):
        """The qTest swagger_client model with detailed information for the given requirement.

        Returns:
            swagger_client.RequirementResource

        Raises:
            RuntimeError: General qTest API failure.
        """

        req_api = swagger_client.RequirementApi()

        try:
            return req_api.get_requirement(self._qtest_project_id, self.qtest_req_id)
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))

    def assert_exists(self):
        """Verify that the given requirement is present in the "Requirements" view.

        Raises:
            AssertionError: Requirement does not exist or could not be created!
        """

        if self._qtest_req_id:
            pass
        elif self._jira_id in self._jira_req_id_cache:
            self._qtest_req_id = self._jira_req_id_cache[self._jira_id]
        else:
            try:
                self._create_req()
            except RuntimeError as e:
                raise AssertionError("Requirement could not be created for '{}'\n{}!".format(self._jira_id, str(e)))

    def assert_linked(self, qtest_test_case_id):
        """Verify that a given qTest test case ID is linked to this requirement.

        Args:
            qtest_test_case_id (int): The qTest test case ID to validate if linked to the current Jira requirement.

        Raises:
            AssertionError: Requirement does not exist or could not be created!
            RuntimeError: General qTest API failure.
        """

        link_api = swagger_client.ObjectlinkApi()

        try:
            links = link_api.find(self._qtest_project_id, 'requirements', ids=[self.qtest_req_id])
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))

        if links:
            qtest_obj_ids = []
            for resource_objects in [link.objects for link in links]:
                for resource_object in resource_objects:
                    qtest_obj_ids.append(resource_object.id)
            assert qtest_test_case_id in qtest_obj_ids
        else:
            raise AssertionError('Requirement is not linked to any other qTest resources!')

    def clean_up(self):
        """Delete the requirement from the qTest project under test.

        Use with caution because if a requirement is deleted that is shared among multiple test cases

        Raises:
            RuntimeError: General qTest API failure.
        """

        if self._qtest_req_id:
            self._qtest_req_id = None
            req_api = swagger_client.RequirementApi()

            try:
                req_api.delete(self._qtest_project_id, self.qtest_req_id)
            except ApiException as e:
                raise RuntimeError("The qTest API reported an error!\n"
                                   "Status code: {}\n"
                                   "Reason: {}\n"
                                   "Message: {}".format(e.status, e.reason, e.body))

            self._purge_req_id_cache(self._jira_id)

    def _create_req(self):
        """Create a qTest requirement for the qTest project under test.

        Raises:
            RuntimeError: General qTest API failure.
        """

        req_api = swagger_client.RequirementApi()
        req_resource = swagger_client.RequirementResource(name=self.name)

        try:
            req_id = req_api.create_requirement(self._qtest_project_id,
                                                req_resource,
                                                parent_id=self._qtest_req_module_id).id
            self._update_req_id_cache(self._jira_id, req_id)
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))

    @classmethod
    def _update_req_id_cache(cls, jira_id, qtest_req_id):
        """Update the requirement ID cache used to track requirements shared between multiple JiraRequirement objects.

        Args:
            jira_id (str): The Jira ticket ID.
            qtest_req_id (int): The qTest resource ID for associated with the given Jira ticket ID.
        """

        cls._jira_req_id_cache[jira_id] = qtest_req_id

    @classmethod
    def _purge_req_id_cache(cls, jira_id):
        """Purge an item from the required ID cache used to track requirements shared between multiple JiraRequirement
        objects.

        Args:
            jira_id (str): The Jira ticket ID to purge from the cache.
        """

        del cls._jira_req_id_cache[jira_id]
