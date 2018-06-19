# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================

from __future__ import absolute_import
import swagger_client
from base64 import b64encode
from datetime import datetime
import re
from zigzag.utility_facade import UtilityFacade
import requests
import json


class ZigZagTestLog(object):

    _TESTCASE_NAME_RGX = re.compile(r'(\w+)(\[.+\])')
    _TESTCASE_GROUP_RGX = re.compile(r'tests\.(test_[\w-]+)\.?(Test\w+)?$')
    _test_run_failure_output_field_id = 0

    def __init__(self, testcase_xml, mediator):
        """Create a TestLog object

        Args:
            testcase_xml (ElementTree): A XML element representing a JUnit style testcase result.
            mediator (ZigZag): the mediator that stores shared data
        """

        self._testcase_xml = testcase_xml
        self._mediator = mediator

        # this is data that will be collected from qTest
        self._qtest_requirements = []
        self._jira_issues = []
        self._qtest_testcase_id = None
        self._failure_output = ''  # hard code this to empty string
        self._parse()
        self._lookup_ids()
        self._mediator.test_logs.append(self)

    @property
    def name(self):
        """Gets the test log name

        Returns:
            str: The name of the test log
        """
        return self._name

    @property
    def qtest_testcase_id(self):
        """Gets the testcase id that corresponds to this test log

        Returns:
            int: The qTest testcase id
            None: The testcase has not been created yet
        """
        if self._qtest_testcase_id is None:
            self._lookup_ids()
        return self._qtest_testcase_id

    @property
    def jira_issues(self):
        """Gets the associated jira issue ids

        Returns:
            list[str]: A list of jira issue ids
        """
        return self._jira_issues

    @property
    def qtest_requirements(self):
        """Gets the qTest requirements ids

        Returns:
            list[int]: a list of associated qTest requirements object IDs
        """
        if not len(self._qtest_requirements):
            self._lookup_requirements()
        return self._qtest_requirements

    @property
    def status(self):
        """Gets the status of this test log

        Return:
            str: the status of this test execution
        """
        return self._status

    @property
    def failure_output(self):
        """Gets the failure output of this test log

        Returns:
            str: The output from failure or error of this test execution
        """
        return self._failure_output

    @property
    def start_date(self):
        """Gets the start date of this test log

        Returns:
            str: the start date of this test execution
        """
        return self._exe_start_date

    @property
    def end_date(self):
        """Gets the end date of this test log

        Returns:
            str: the end date of this test execution
        """
        return self._exe_end_date

    @property
    def automation_content(self):
        """Gets the automation content of this test log

        Returns:
            str: The UUID that we associate with this Test Case
        """
        return self._automation_content

    @property
    def test_run_failure_output_field_id(self):
        """Gets the failure output field id

        Returns:
            int: The id of the 'Failure Output' field for test-run objects
        """
        return self._get_test_run_failure_output_field_id(self._mediator)

    @property
    def module_hierarchy(self):
        """Gets the module hierarchy to be used by qtest.

        Returns:
            list(str): An ordered list of strings to use for the qTest results hierarchy.

        Raises:
            RuntimeError: the testcase 'classname' attribute is invalid
        """
        testsuite_props = self._mediator.testsuite_props
        module_hierarchy = [testsuite_props['RPC_RELEASE'],             # RPC Release Version (e.g. 16.0.0)
                            testsuite_props['JOB_NAME'],                # CI Job name (e.g. PM_rpc-openstack-pike-xenial_mnaio_no_artifacts-swift-system) # noqa
                            testsuite_props['MOLECULE_TEST_REPO'],      # (e.g. molecule-validate-neutron-deploy)
                            testsuite_props['MOLECULE_SCENARIO_NAME']]  # (e.g. "default")

        try:
            testcase_groups = ZigZagTestLog._TESTCASE_GROUP_RGX.search(
                self._testcase_xml.attrib['classname']).groups()
        except AttributeError:
            raise RuntimeError("Test case '{}' has an invalid 'classname' attribute!".format(
                self._testcase_xml.attrib['classname']))

        module_hierarchy.append(testcase_groups[0])         # Always append at least the filename of the test grouping.
        if testcase_groups[1]:
            module_hierarchy.append(testcase_groups[1])     # Append the class name of tests if specified.

        return module_hierarchy

    @property
    def qtest_test_log(self):
        """Gets a qTest AutomationTestLogResource

        Returns:
            AutomationTestLogResource: a qTest swagger client object
        """
        date_time_now = datetime.utcnow()
        log = swagger_client.AutomationTestLogResource()
        log.properties = [
            swagger_client.PropertyResource(field_id=self.test_run_failure_output_field_id,
                                            field_value=self._failure_output)]
        log.name = self._name
        log.automation_content = self._automation_content
        log.exe_start_date = self._exe_start_date
        log.exe_end_date = self._exe_end_date
        log.build_url = self._mediator.build_url
        log.build_number = self._mediator.build_number
        log.module_names = self.module_hierarchy
        log.status = self._status
        log.attachments = \
            [swagger_client.AttachmentResource(name="junit_{}.xml".format(date_time_now.strftime('%Y-%m-%dT%H-%M')),
                                               content_type='application/xml',
                                               data=b64encode(self._mediator.serialized_junit_xml).decode('UTF-8'),
                                               author={})]
        return log

    def _parse(self):
        """Parse the _testcase_xml
        """
        self._status = 'PASSED'

        if self._testcase_xml.find('failure') is not None or self._testcase_xml.find('error') is not None:
            self._status = 'FAILED'

            if self.test_run_failure_output_field_id is not None:
                possible_messages = [self._testcase_xml.find('error'), self._testcase_xml.find('failure')]
                message = "\n".join([x.attrib['message'] for x in possible_messages if x is not None])
                self._failure_output = message

        elif self._testcase_xml.find('skipped') is not None:
            self._status = 'SKIPPED'

        try:
            self._name = ZigZagTestLog._TESTCASE_NAME_RGX.match(self._testcase_xml.attrib['name']).group(1)
            self._automation_content = \
                self._testcase_xml.find("./properties/property/[@name='test_id']").attrib['value']
            self._jira_issues = \
                [jira.get('value') for jira in self._testcase_xml.findall("./properties/property/[@name='jira']")]
            self._exe_start_date = \
                self._testcase_xml.find("./properties/property/[@name='start_time']").attrib['value']
            self._exe_end_date = self._testcase_xml.find("./properties/property/[@name='end_time']").attrib['value']
        except AttributeError:
            raise RuntimeError("Test case '{}' is missing the required property!".format(self.name))

    def _lookup_ids(self):
        """Search for testcase id by automation content

        Using the 'requests' library gets us around the bugs in the Swagger client
        If the API response contains no items _qtest_testcase_id will be None
        """
        headers = {'Authorization': self._mediator.qtest_api_token,
                   'Content-Type': 'application/json'}
        endpoint = "https://apitryout.qtestnet.com/api/v3/projects/{}/search?pageSize=100&page=1".format(
            self._mediator.qtest_project_id
        )
        body = {
            "object_type": "test-cases",
            "fields": [
                "id"
            ],
            "query": "'Automation Content' = '{}'".format(self.automation_content)
        }
        try:
            r = requests.post(endpoint, data=json.dumps(body), headers=headers)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n".format(e.response.status_code, e.response.reason))
        parsed = json.loads(r.text)
        try:
            self._qtest_testcase_id = parsed['items'][0]['id']
        except IndexError:  # test case has not been created yet in qTest
            pass

    def _lookup_requirements(self):
        """finds an exact matches for all requirements imported from jira associated with this log
        The Jira id is stored on a requirements name ex: 'PRO-18404 Zach's requirement'

        Using the 'requests' library gets us around the bugs in the Swagger client
        If the API response contains no items _qtest_requirements will be an empty list
        """
        for jira_id in self._jira_issues:
            headers = {'Authorization': self._mediator.qtest_api_token,
                       'Content-Type': 'application/json'}
            endpoint = "https://apitryout.qtestnet.com/api/v3/projects/{}/search?pageSize=100&page=1".format(
                self._mediator.qtest_project_id
            )
            query = "'name' ~ '{}'".format(jira_id)
            body = {
                "object_type": "requirements",
                "fields": [
                    "id",
                    "name"
                ],
                "query": "{}".format(query)
            }
            try:
                r = requests.post(endpoint, data=json.dumps(body), headers=headers)
                r.raise_for_status()
                parsed = json.loads(r.text)
            except requests.exceptions.RequestException as e:
                raise RuntimeError("The qTest API reported an error!\n"
                                   "Status code: {}\n"
                                   "Reason: {}\n"
                                   "Message: {}".format(e.status, e.reason, e.body))
            exact_jira_regex = re.compile('([a-zA-Z]+-\d+)')
            if parsed['total'] == 1:
                self._qtest_requirements.append(parsed['items'][0]['id'])
            elif parsed['total'] > 1:
                for requirement in parsed['items']:
                    if exact_jira_regex.match(requirement['name']).group(1) == jira_id:
                        self._qtest_requirements.append(requirement['id'])

    @classmethod
    def _get_test_run_failure_output_field_id(cls, mediator):
        """Gets the test_run_failure_output_field_id from this class

        Args:
            mediator (ZigZag): The ZigZag mediator

        Returns:
            int: The ID for test_run_failure_output_field_id
        """
        if cls._test_run_failure_output_field_id == 0:
            cls._test_run_failure_output_field_id = \
                UtilityFacade(mediator).find_custom_field_id_by_label('Failure Output', 'test-runs')
        return cls._test_run_failure_output_field_id
