# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import swagger_client
from swagger_client.rest import ApiException


class RequirementsLinkFacade(object):

    def __init__(self, mediator):
        """A facade to link requirements to test-cases

        Args:
            mediator (ZigZag): the mediator that stores shared data
        """
        self._mediator = mediator
        self._object_link_api = swagger_client.ObjectlinkApi()

    def link(self):
        """links known test requirements(jira tickets) to known test cases in qTest

        Raises:
            RuntimeError: The qTest API reported an error!
        """

        # build data structure to control linking dict[str: list]
        links = {}
        for log in self._mediator.test_logs:
            for requirement in log.qtest_requirements:
                if requirement in links:
                    links[requirement].append(log.qtest_testcase_id)
                else:
                    links[requirement] = []
                    if log.qtest_testcase_id:
                        links[requirement].append(log.qtest_testcase_id)

        for requirement, test_case_ids in links.items():
            if len(test_case_ids):
                self._link_requirement_to_testcases(requirement, test_case_ids)

    def _link_requirement_to_testcases(self, requirement_id, test_case_ids):
        """Links a test_case to a set of requirements in qTest

        Args:
            requirement_id (int): the qTest test case id
            test_case_ids (list): the qTest requirement ids

        Raises:
            RuntimeError: The qTest API reported an error!
        """
        try:
            self._object_link_api.link_artifacts(self._mediator.qtest_project_id, 'requirements',
                                                 'test-cases', test_case_ids, requirement_id)
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))
