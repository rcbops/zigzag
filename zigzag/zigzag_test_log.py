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
from zigzag.module_hierarchy_facade import ModuleHierarchyFacade
from zigzag.link_generation_facade import LinkGenerationFacade


class ZigZagTestLog(object):

    _TESTCASE_NAME_RGX = re.compile(r'(^[\w-]+)')
    _test_run_failure_output_field_id = 0
    _fields = 0
    _failure_link_field_id = 0
    _test_sha_field_id = 0

    def __init__(self, testcase_xml, mediator):
        """Create a TestLog object

        Args:
            testcase_xml (ElementTree): A XML element representing a JUnit style testcase result.
            mediator (ZigZag): the mediator that stores shared data
        """

        self._exe_end_date = None
        self._exe_start_date = None

        self._testcase_xml = testcase_xml
        self._mediator = mediator
        self._module_hierarchy_facade = ModuleHierarchyFacade(testcase_xml, mediator)

        # this is data that will be collected from qTest
        self._qtest_requirements = []
        self._jira_issues = []
        self._qtest_testcase_id = None

        self._failure_output = ''  # hard code this to empty string
        self._full_failure_output = ''
        self._def_line_number = ''
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
    def full_failure_output(self):
        """Gets the full failure output of this test log

        Returns:
            str: The output from failure or error of this test execution
        """
        return self._full_failure_output

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
    def fields(self):
        """Gets the fields dict of ZigZagTestLogFields

        Returns:
            dict(str: ZigZagTestLogField) all the configured fields for a testlog object
        """
        return self._get_fields(self._mediator)

    @property
    def module_hierarchy(self):
        """Gets the module hierarchy to be used by qtest.

        Returns:
            list(str): An ordered list of strings to use for the qTest results hierarchy.

        Raises:
            RuntimeError: the testcase 'classname' attribute is invalid
        """
        return self._module_hierarchy_facade.get_module_hierarchy()

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
        # Attach all test suite properties to the log
        # noinspection PyUnresolvedReferences
        for name, field in list(self.fields.items()):
            log.properties.append(swagger_client.PropertyResource(field_id=field['id'],
                                                                  field_value=field['value']
                                                                  ))
        if self.status == 'FAILED' and self.failure_link_field_id:
            log.properties.append(swagger_client.PropertyResource(field_id=self.failure_link_field_id,
                                                                  field_value=self.github_failure_link))
        # Attach SHA
        if self.test_sha_field_id and self.link_generation_facade.git_sha:
            log.properties.append(swagger_client.PropertyResource(field_id=self.test_sha_field_id,
                                                                  field_value=self.link_generation_facade.git_sha))
        log.name = self._name
        log.automation_content = self._automation_content

        if self._exe_start_date:
            log.exe_start_date = self._exe_start_date
        else:
            log.exe_start_date = date_time_now.strftime('%Y-%m-%dT%H:%M:%SZ')
        if self._exe_end_date:
            log.exe_end_date = self._exe_end_date
        else:
            log.exe_end_date = date_time_now.strftime('%Y-%m-%dT%H:%M:%SZ')
        log.build_url = self._mediator.build_url
        log.build_number = self._mediator.build_number
        log.module_names = self.module_hierarchy
        log.full_fail_log_text = self._full_failure_output
        log.attachment_suffix = date_time_now.strftime('%Y-%m-%dT%H-%M')
        log.status = self._status
        log.attachments = \
            [swagger_client.AttachmentResource(name="junit_{}.xml".format(log.attachment_suffix),
                                               content_type='application/xml',
                                               data=b64encode(self._mediator.serialized_junit_xml).decode('UTF-8'),
                                               author={})]
        if log.full_fail_log_text:
            log.attachments.append(
                swagger_client.AttachmentResource(name="failure_output_{}.txt".format(log.attachment_suffix),
                                                  content_type='text/plain',
                                                  data=b64encode(
                                                      log.full_fail_log_text.encode('UTF-8')).decode('UTF-8'),
                                                  author={}))
        return log

    @property
    def github_failure_link(self):
        """Gets the Link to the testcase failure if one exists

        Returns:
            str: The link to the failure
            None
        """
        return self.link_generation_facade.github_testlog_failure_link(self)

    @property
    def link_generation_facade(self):
        """Gets the instance attached to the class of
        LinkGenerationFacade

        Returns:
            LinkGenerationFacade
        """
        return self._get_link_generation_facade(self._mediator)

    @property
    def test_file(self):
        """Gets the file that contains the test that generated this log

        Returns:
            str: the path to this file
        """
        return self._test_file

    @property
    def failure_link_field_id(self):
        """Gets the failure output field id

        Returns:
            int: The id of the 'Failure Link' field for test-run objects
        """
        return self._get_failure_link_field_id(self._mediator)

    @property
    def def_line_number(self):
        """Gets the line number of the test def

        Returns:
            str: The line number of the test definition
        """
        return self._def_line_number

    @property
    def test_sha_field_id(self):
        """Gets the Test SHA field id

        Returns:
            int: The id of the 'Test SHA' field for test-run objects
        """
        return self._get_test_sha_field_id(self._mediator)

    def _parse(self):
        """Parse the _testcase_xml"""

        self._status = 'PASSED'

        all_failures = self._testcase_xml.findall('failure') + self._testcase_xml.findall('error')
        if len(all_failures):
            self._status = 'FAILED'

            if self.test_run_failure_output_field_id is not None:
                errors = self._testcase_xml.findall('error')
                failures = self._testcase_xml.findall('failure')
                possible_messages = errors + failures
                message = "\n".join([element.text for element in possible_messages if element is not None])

                self._full_failure_output = message
                self._failure_output = self._get_truncated_failure_output(message)
        elif self._testcase_xml.find('skipped') is not None:
            self._status = 'SKIPPED'

        try:  # Required
            self._name = ZigZagTestLog._TESTCASE_NAME_RGX.match(self._testcase_xml.attrib['name']).group(0)
            self._automation_content = self._find_property('test_id')
            self._jira_issues = \
                [jira.get('value') for jira in self._testcase_xml.findall("./properties/property/[@name='jira']")]
            self._exe_start_date = self._find_property('start_time')
        except AttributeError:
            raise RuntimeError("Test case '{}' is missing the required property!".format(self.name))

        try:  # Optional
            self._exe_end_date = self._find_property('end_time')  # Its possible for a case to not have an end date
            self._test_file = self._testcase_xml.attrib['file']
            self._def_line_number = self._testcase_xml.attrib['line']
        except AttributeError:
            pass

    def _find_property(self, name):
        """A helper to find a property by name

        Args:
            name (str): The name of the property you want to fin

        Returns:
            str: The value of the property
        """
        return self._testcase_xml.find("./properties/property/[@name='{}']".format(name)).attrib['value']

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
                # noinspection PyUnresolvedReferences
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

    @classmethod
    def _get_fields(cls, mediator):
        """Gets the fields from this class

        Args:
            mediator (ZigZag): The ZigZag mediator

        Returns:
            dict(str: ZigZagTestLogField)
        """

        if cls._fields == 0:
            cls._fields = {}
            for prop, value in list(mediator.testsuite_props.items()):
                f = {
                    'id': UtilityFacade(mediator).find_custom_field_id_by_label(prop, 'test-runs'),
                    'name': prop,
                    'value': value
                }
                if f['id']:
                    cls._fields[prop] = f

        return cls._fields

    @classmethod
    def _get_link_generation_facade(cls, mediator):
        """Get The instance of LinkGenerationFacade

        Args:
            mediator (ZigZag): The ZigZag mediator

        Returns:
            LinkGenerationFacade
        """
        return LinkGenerationFacade(mediator)

    @classmethod
    def _get_failure_link_field_id(cls, mediator):
        """Gets the failure_link_field_id from this class

        Args:
            mediator (ZigZag): The ZigZag mediator

        Returns:
            int: The ID for failure_link_field_id
        """
        if cls._failure_link_field_id == 0:
            cls._failure_link_field_id = \
                UtilityFacade(mediator).find_custom_field_id_by_label('Failure Link', 'test-runs')
        return cls._failure_link_field_id

    @classmethod
    def _get_test_sha_field_id(cls, mediator):
        """Gets the test_sha_field_id from this class

        Args:
            mediator (ZigZag): The ZigZag mediator

        Returns:
            int: The ID for test_sha_field_id
        """
        if cls._test_sha_field_id == 0:
            cls._test_sha_field_id = \
                UtilityFacade(mediator).find_custom_field_id_by_label('Test SHA', 'test-runs')
        return cls._test_sha_field_id

    @classmethod
    def _get_truncated_failure_output(cls, message):
        """Process failure/error messages to produce a truncated version of the message for readability in the qTest
        interface.

        Args:
            message (str): Message to process.

        Returns:
            str: Truncated failure message.
        """

        max_lines = 3
        max_line_length = 120
        msg_line_count = len(message.split('\n'))
        # Throw out the useless last 2 lines of the message if over a certain length.
        # Note: pytest failure messages follow a predictable pattern, hence why we can toss lines without inspection.
        msg_lines = message.split('\n')[msg_line_count - (max_lines + 2):msg_line_count - 2] \
            if msg_line_count > (max_lines + 2) else [message]
        truncated_message = 'Log truncated, please see attached failure log for more details...\n' \
            if len(msg_lines) == max_lines else ''

        for line in msg_lines:
            truncated_message += line + '\n' if len(line) <= max_line_length else line[:max_line_length] + '...\n'

        return truncated_message.rstrip()
