# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import re
import json
import requests
import swagger_client
from base64 import b64encode
from datetime import datetime
from future.moves.collections import Sequence
from zigzag.utility_facade import UtilityFacade
from zigzag.link_generation_facade import LinkGenerationFacade

SWEET_UNICORN_GIF = 'https://media.giphy.com/media/g6i1lEax9Pa24/giphy.gif'


# ======================================================================================================================
# Classes
# ======================================================================================================================
class _ZigZagTestLog(object):

    _TESTCASE_NAME_RGX = re.compile(r'(^[\w-]+)')
    _test_run_failure_output_field_id = 0
    _fields = 0
    _failure_link_field_id = 0
    _test_sha_field_id = 0
    _date_time_format = '%Y-%m-%dT%H:%M:%SZ'  # the highest degree of accuracy that qtest will accept (no micro seconds)

    def __init__(self, testcase_xml, mediator):
        """Create a TestLog object.

        Args:
            testcase_xml (ElementTree): A XML element representing a JUnit style testcase result.
            mediator (ZigZag): The mediator that stores shared data.
        """

        self._end_date = None
        self._start_date = None

        self._testcase_xml = testcase_xml
        self._mediator = mediator

        # this is data that will be collected from qTest
        self._qtest_requirements = []  # lazy loaded & simple cache
        self._qtest_testcase_id = None
        self._test_execution_parameters = None

        self._stdout = None
        self._stderr = None

        self._status = None
        self._test_file = None
        self._classname = None
        self._failure_output = None
        self._def_line_number = None
        self._automation_content = None
        self._full_failure_output = None
        self._name = None
        self._errors = None
        self._failures = None

        self._jira_issues = None
        self._qtest_property_resource_list = None
        self._qtest_attachment_list = None
        self._date_time_now = datetime.utcnow()  # use same time for all operations

    @property
    def name(self):
        """Gets the test log name

        Returns:
            str: The name of the test log
        """
        if self._name is None:
            try:
                self._name = _ZigZagTestLog._TESTCASE_NAME_RGX.match(self._testcase_xml.attrib['name']).group(0)
            except AttributeError:
                raise RuntimeError("Test case '{}' is missing the required property name!".format(self._name))

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
    def test_execution_parameters(self):
        """ Gets the array of job config attributes
            annotated at the end of a job name.

        Returns:
            List: of job attributes.
        """
        if self._test_execution_parameters is None:
            self._test_execution_parameters = self._lookup_test_execution_parameters(",")
        return self._test_execution_parameters

    @property
    def jira_issues(self):
        """Gets the associated jira issue ids

        Returns:
            list[str]: A list of jira issue ids
        """
        if self._jira_issues is None:
            try:
                self._jira_issues = \
                    [jira.get('value') for jira in self._testcase_xml.findall("./properties/property/[@name='jira']")]
            except AttributeError:
                raise RuntimeError("Test case '{}' is missing the required property!".format(self._name))

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
        if self._status is None:
            self._status = 'PASSED'
            try:
                all_failures = self.failures + self.errors
                if len(all_failures):
                    self._status = 'FAILED'
                elif self._testcase_xml.find('skipped') is not None:
                    self._status = 'SKIPPED'
            except AttributeError:
                self._status = ''

        return self._status

    @property
    def stderr(self):
        """Gets the contents of 'stderr' if captured.

        Return:
            str: output printed to 'stderr'
        """

        if self._stderr is None:
            try:
                self._stderr = self._testcase_xml.find('system-err').text
            except AttributeError:
                self._stderr = ''

        return self._stderr

    @property
    def stdout(self):
        """Gets the contents of 'stdout' if captured.

        Return:
            str: output printed to 'stdout'
        """

        if self._stdout is None:
            try:
                self._stdout = self._testcase_xml.find('system-out').text
            except AttributeError:
                self._stdout = ''

        return self._stdout

    @property
    def failure_output(self):
        """Gets the failure output of this test log

        Returns:
            str: The output from failure or error of this test execution
        """
        if self._failure_output is None:
            max_lines = 3
            max_line_length = 120
            msg_line_count = len(self.full_failure_output.split('\n'))
            # Throw out the useless last 2 lines of the message if over a certain length.
            # Note: pytest failure messages follow a predictable pattern, hence why we can toss lines without inspection
            msg_lines = self.full_failure_output.split('\n')[msg_line_count - (max_lines + 2):msg_line_count - 2] \
                if msg_line_count > (max_lines + 2) else [self.full_failure_output]
            truncated_message = 'Log truncated, please see attached failure log for more details...\n' \
                if len(msg_lines) == max_lines else ''

            for line in msg_lines:
                truncated_message += line + '\n' if len(line) <= max_line_length else line[:max_line_length] + '...\n'

            self._failure_output = truncated_message.rstrip()
        return self._failure_output

    @property
    def errors(self):
        """Gets the errors form the testcase_xml

        Returns:
            list: the list of errors found
        """
        if self._errors is None:
            self._errors = self._testcase_xml.findall('error')

        return self._errors

    @property
    def failures(self):
        """Gets the failures from the testcase_xml

        Returns:
            list: the list of failures found
        """
        if self._failures is None:
            self._failures = self._testcase_xml.findall('failure')

        return self._failures

    @property
    def full_failure_output(self):
        """Gets the full failure output of this test log

        Returns:
            str: The output from failure or error of this test execution
        """
        if self._full_failure_output is None:
            possible_messages = self.errors + self.failures
            if len(possible_messages):
                if self.test_run_failure_output_field_id is not None:
                    message = "\n".join([element.text for element in possible_messages if element is not None])
                    self._full_failure_output = message
            else:
                self._full_failure_output = ''  # hard code this to empty string
        return self._full_failure_output

    @property
    def start_date(self):
        """Gets the start date of this test log

        Returns:
            str: the start date of this test execution
        """
        if self._start_date is None:
            try:
                self._start_date = self._find_property('start_time')
            except AttributeError:
                self._start_date = self._date_time_now.strftime(self._date_time_format)

        return self._start_date

    @property
    def end_date(self):
        """Gets the end date of this test log

        Returns:
            str: the end date of this test execution
        """
        if self._end_date is None:
            try:
                self._end_date = self._find_property('end_time')
            except AttributeError:
                self._end_date = self._date_time_now.strftime(self._date_time_format)

        return self._end_date

    @property
    def automation_content(self):
        """Gets the automation content of this test log

        Returns:
            str: The UUID that we associate with this Test Case
        """
        if self._automation_content is None:
            try:
                self._automation_content = self._find_property('test_id')
            except AttributeError:
                message = "Test case '{}' is missing the required property! automation content".format(self._name)
                raise ZigZagTestLogError(message)
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

        return self._mediator.config_dict.get_config('module_hierarchy', self)

    @property
    def test_file(self):
        """Gets the test_file property

        Returns:
            str: the file containing the test that generated the xml
        """
        if self._test_file is None:
            self._test_file = self._testcase_xml.attrib['file']

        return self._test_file

    @property
    def classname(self):
        """Gets the classname property

        Returns:
            str: the classname of the test
        """
        if self._classname is None:
            self._classname = self._testcase_xml.attrib['classname']

        return self._classname

    @property
    def def_line_number(self):
        """Gets the def_line_number

        Returns:
            str: the sting that is the def_line_number
        """
        if self._def_line_number is None:
            self._def_line_number = self._testcase_xml.attrib['line']

        return self._def_line_number

    @property
    def qtest_property_resource_list(self):
        """Gets the list of qtest properties

        Returns:
            list: the list of swagger_client.PropertyResource
        """

        properties = []

        if self._qtest_property_resource_list is None:
            properties.append(swagger_client.PropertyResource(field_id=self.test_run_failure_output_field_id,
                                                              field_value=self.failure_output))
            # Attach all test suite properties to the log
            # noinspection PyUnresolvedReferences
            for name, field in list(self.fields.items()):
                properties.append(swagger_client.PropertyResource(field_id=field['id'],
                                                                  field_value=field['value']
                                                                  ))
            if self.failure_link_field_id:
                link = None
                if self.status == 'FAILED':
                    link = self.github_failure_link
                if not link:
                    link = SWEET_UNICORN_GIF
                properties.append(swagger_client.PropertyResource(field_id=self.failure_link_field_id,
                                                                  field_value=link))
            # Attach SHA
            if self.test_sha_field_id and self.link_generation_facade.git_sha:
                properties.append(swagger_client.PropertyResource(field_id=self.test_sha_field_id,
                                                                  field_value=self.link_generation_facade.git_sha))
            self._qtest_property_resource_list = properties

        return self._qtest_property_resource_list

    @property
    def qtest_attachment_list(self):
        """Gets the list of qtest attachments

        Returns:
            list: the list of swagger_client.AttachmentResource
        """

        attachments = []

        if self._qtest_attachment_list is None:
            attachment_suffix = self._date_time_now.strftime('%Y-%m-%dT%H-%M')
            encoded_xml = b64encode(self._mediator.serialized_junit_xml).decode('UTF-8')
            attachments.append(
                swagger_client.AttachmentResource(name="junit_{}.xml".format(attachment_suffix),
                                                  content_type='application/xml',
                                                  data=encoded_xml,
                                                  author={}))
            if self.full_failure_output:
                encoded_output = b64encode(self.full_failure_output.encode('UTF-8')).decode('UTF-8')
                attachments.append(
                    swagger_client.AttachmentResource(name="failure_output_{}.txt".format(attachment_suffix),
                                                      content_type='text/plain',
                                                      data=encoded_output,
                                                      author={}))
            if self.status == 'FAILED' and self.stderr:
                encoded_stderr = b64encode(self.stderr.encode('UTF-8')).decode('UTF-8')
                attachments.append(
                    swagger_client.AttachmentResource(name="stderr_{}.txt".format(attachment_suffix),
                                                      content_type='text/plain',
                                                      data=encoded_stderr,
                                                      author={}))
            if self.status == 'FAILED' and self.stdout:
                encoded_stdout = b64encode(self.stdout.encode('UTF-8')).decode('UTF-8')
                attachments.append(
                    swagger_client.AttachmentResource(name="stdout_{}.txt".format(attachment_suffix),
                                                      content_type='text/plain',
                                                      data=encoded_stdout,
                                                      author={}))

        return attachments

    @property
    def qtest_test_log(self):
        """Gets a qTest AutomationTestLogResource

        Returns:
            swagger_client.AutomationTestLogResource
        """
        log = swagger_client.AutomationTestLogResource()
        log.properties = self.qtest_property_resource_list
        log.name = self.name
        log.automation_content = self.automation_content
        log.exe_start_date = self.start_date
        log.exe_end_date = self.end_date
        log.build_url = self._mediator.build_url
        log.build_number = self._mediator.build_number
        log.module_names = self.module_hierarchy
        log.full_fail_log_text = self.full_failure_output
        log.attachment_suffix = self._date_time_now.strftime('%Y-%m-%dT%H-%M')
        log.status = self.status
        log.attachments = self.qtest_attachment_list

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
    def failure_link_field_id(self):
        """Gets the failure output field id

        Returns:
            int: The id of the 'Failure Link' field for test-run objects
        """
        return self._get_failure_link_field_id(self._mediator)

    @property
    def test_sha_field_id(self):
        """Gets the Test SHA field id

        Returns:
            int: The id of the 'Test SHA' field for test-run objects
        """
        return self._get_test_sha_field_id(self._mediator)

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

    def _lookup_test_execution_parameters(self, delimiter):
        """ Finds the array of job config attributes on the end of the job name. In some cases,
            a test runner will place a leading delmiter before the elements. If that's the case,
            we drop the frist caracter in the string before we split it.

        Returns:
            List: of job config attributes.
        """
        full_name = self._testcase_xml.attrib['name']
        delimited_list = full_name[full_name.find("[")+1:full_name.find("]")]
        test_execution_parameter_list = delimited_list.split(delimiter) if "[" in full_name else []
        return test_execution_parameter_list

    def _lookup_requirements(self):
        """finds an exact matches for all requirements imported from jira associated with this log
        The Jira id is stored on a requirements name ex: 'PRO-18404 Zach's requirement'

        Using the 'requests' library gets us around the bugs in the Swagger client
        If the API response contains no items _qtest_requirements will be an empty list
        """
        for jira_id in self.jira_issues:
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
            exact_jira_regex = re.compile(r'([a-zA-Z]+-\d+)')
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


class _ZigZagTestLogWithSteps(_ZigZagTestLog):
    def __init__(self, testcase_name, teststeps_xml, mediator):
        """Create a TestLog object that contains steps.

        Args:
            testcase_name (str): The name of the test case.
            teststeps_xml (list(ElementTree)): A list of JUnit style testcase XML elements representing test steps for
                a single qTest test log.
            mediator (ZigZag): The mediator that stores shared data.
        """

        super(_ZigZagTestLogWithSteps, self).__init__(teststeps_xml[0], mediator)

        self._name = testcase_name
        self._teststeps_xml = teststeps_xml
        self._zz_test_step_logs = []
        self._qtest_test_step_logs = []

        # Convert the test steps into test logs for easier post-processing.
        self._zz_test_step_logs = [_ZigZagTestLog(ts_xml, self._mediator) for ts_xml in self._teststeps_xml]

    @property
    def errors(self):
        """Gets the errors form the testcase_xml

        Returns:
            list: the list of errors found
        """
        if self._errors is None:
            self._errors = [error for log in self._zz_test_step_logs for error in log.errors]

        return self._errors

    @property
    def failures(self):
        """Gets the failures from the testcase_xml

        Returns:
            list: the list of failures found
        """
        if self._failures is None:
            self._failures = [failure for log in self._zz_test_step_logs for failure in log.failures]

        return self._failures

    @property
    def status(self):
        """Gets the status of this test log

        Return:
            str: the status of this test execution
        """
        if self._status is None:
            statuses = [log.status for log in self._zz_test_step_logs]
            if any([status == 'FAILED' for status in statuses]):
                self._status = 'FAILED'
            elif any([status == 'SKIPPED' for status in statuses]):
                self._status = 'SKIPPED'
            else:
                self._status = 'PASSED'

        return self._status

    @property
    def stderr(self):
        """Gets the contents of 'stderr' if captured.

        Return:
            str: output printed to 'stderr'
        """

        if self._stderr is None:
            for log in self._zz_test_step_logs:
                if log.stderr:
                    self._stderr = log.stderr
                    break

        return self._stderr

    @property
    def stdout(self):
        """Gets the contents of 'stdout' if captured.

        Return:
            str: output printed to 'stdout'
        """

        if self._stdout is None:
            for log in self._zz_test_step_logs:
                if log.stdout:
                    self._stdout = log.stdout
                    break

        return self._stdout

    @property
    def failure_output(self):
        """Gets the failure output of this test log

        Returns:
            str: The output from failure or error of this test execution
        """
        if self._failure_output is None:
            for log in self._zz_test_step_logs:
                if log.status == 'FAILED':
                    self._failure_output = log.failure_output

        return self._failure_output

    @property
    def full_failure_output(self):
        """Gets the full failure output of this test log

        Returns:
            str: The output from failure or error of this test execution
        """
        if self._full_failure_output is None:
            if self.status == 'FAILED':
                for log in self._zz_test_step_logs:
                    if log.status == 'FAILED':
                        self._full_failure_output = log.full_failure_output
                        break  # take the first full_failure_output
            else:
                self._full_failure_output = ''

        return self._full_failure_output

    @property
    def qtest_test_log(self):
        """Gets a qTest AutomationTestLogResource

        Returns:
            swagger_client.AutomationTestLogResource
        """

        log = super(_ZigZagTestLogWithSteps, self).qtest_test_log
        log.test_step_logs = self.qtest_test_step_logs

        return log

    @property
    def start_date(self):
        """Gets the start date of this test log

        Returns:
            str: the start date of this test execution
        """
        if self._start_date is None:
            # Start of first step
            self._start_date = self._zz_test_step_logs[0].start_date

        return self._start_date

    @property
    def end_date(self):
        """Gets the end date of this test log

        Returns:
            str: the end date of this test execution
        """
        if self._end_date is None:
            # End of last step
            self._end_date = self._zz_test_step_logs[-1].end_date

        return self._end_date

    @property
    def classname(self):
        """Gets the classname property

        Returns:
            str: the classname of the test
        """
        if self._classname is None:
            # Get tricky with the classname by reading the first step and stripping the test name.
            self._classname = self._teststeps_xml[0].attrib['classname'].replace(".{}".format(self.name), '')

        return self._classname

    @property
    def qtest_test_step_logs(self):
        """generates qtest AutomationTestStepLog objects.

        Raises:
            RuntimeError: Test case missing required property.

        Returns:
            list: a list of AutomationTestStepLog
        """
        qtest_test_step_logs = []
        for zz_test_step_log, order in zip(self._zz_test_step_logs, range(len(self._zz_test_step_logs))):
            qtest_test_step_log = swagger_client.AutomationTestStepLog()

            # set the status based on the previous status
            previous_position = order - 1 if order != 0 else 0
            previous_status = self._zz_test_step_logs[previous_position].status
            if zz_test_step_log.status == 'FAILED':
                qtest_test_step_log.status = 'FAILED'
            elif previous_status == 'FAILED' or previous_status == 'SKIPPED' or zz_test_step_log.status == 'SKIPPED':
                qtest_test_step_log.status = 'SKIPPED'
            else:
                qtest_test_step_log.status = 'PASSED'

            qtest_test_step_log.order = order
            qtest_test_step_log.description = zz_test_step_log.name
            qtest_test_step_log.attachments = []
            qtest_test_step_log.expected_result = 'pass'
            if zz_test_step_log.status == 'FAILED':
                # Attach the failure log along with stderr and stdout to the test step if the exist.
                qtest_test_step_log.attachments = zz_test_step_log.qtest_test_log.attachments[1:]
                qtest_test_step_log.actual_result = zz_test_step_log.failure_output
            else:
                qtest_test_step_log.actual_result = qtest_test_step_log.status
            qtest_test_step_logs.append(qtest_test_step_log)

        return qtest_test_step_logs


class ZigZagTestLogs(Sequence):
    def __init__(self, mediator):
        """Create test logs.

        Args:
            mediator (ZigZag): The mediator that stores shared data.
        """

        self._mediator = mediator
        self._test_logs = []

        self._parse_test_cases_with_steps()
        self._parse_test_cases_without_steps()

        self._mediator.test_logs = self

    def count(self, value):
        """Return the number of times x appears in the list.

        Args:
            value (object): Desired value to search for within the list.

        Returns:
            int: number of times 'value' appears in the list.
        """

        return self._test_logs.count(value)

    def index(self, value, start=None, stop=None):
        """Return zero-based index in the list of the first item whose value is equal to 'value'.

        The optional arguments start and stop are interpreted as in the slice notation and are used to limit the search
        to a particular subsequence of the list. The returned index is computed relative to the beginning of the full
        sequence rather than the start argument.

        Args:
            value (object): Desired value to search for within the list.
            start (int): Starting slice index. (Optional)
            stop (int): Ending slice index. (Optional)

        Returns:
            int: Zero-based index in the list of the first item whose value is equal to 'value'

        Raises:
            ValueError: No such value exists in collection.
        """

        return self._test_logs.index(value, start, stop)

    def __reversed__(self):
        """Sequence ABC override."""

        return self._test_logs.__reversed__()

    def __contains__(self, item):
        """Sequence ABC override."""

        return self._test_logs.__contains__(item)

    def __getitem__(self, key):
        """Sequence ABC override."""

        return self._test_logs.__getitem__(key)

    def __iter__(self):
        """Sequence ABC override."""

        return iter(self._test_logs)

    def __len__(self):
        """Sequence ABC override."""

        return len(self._test_logs)

    def _parse_test_cases_with_steps(self):
        """Parse the JUnitXML for test cases that are marked as steps."""

        tc_group_rgx = self._mediator.utility_facade.testcase_group_rgx
        testcases_with_steps_xml = {}

        for testcase_xml in self._find_test_step_test_cases(True):
            tc_name = tc_group_rgx.search(testcase_xml.attrib['classname']).group(2)

            if tc_name in testcases_with_steps_xml:
                testcases_with_steps_xml[tc_name].append(testcase_xml)
            else:
                testcases_with_steps_xml[tc_name] = [testcase_xml]

        for tc_name in testcases_with_steps_xml:
            self._test_logs.append(_ZigZagTestLogWithSteps(tc_name, testcases_with_steps_xml[tc_name], self._mediator))

    def _parse_test_cases_without_steps(self):
        """Parse the JUnitXML for test cases that are NOT marked as steps."""

        for testcase_xml in self._find_test_step_test_cases(False):
            try:
                self._test_logs.append(_ZigZagTestLog(testcase_xml, self._mediator))
            except ZigZagTestLogError:
                pass  # TODO log this error because we cant process this log

    def _find_test_step_test_cases(self, test_step_property_value):
        """Find test_step testcases

        Args:
            test_step_property_value (bool): the value to look for

        Returns:
            list: the list of testcases

        Raises:
            ZigZagTestLogError: when a case is found that does not implement test_steps
        """

        testcases_with_steps_xpath = ".//property/[@name='test_step'][@value='{}']/../..".format(
            str(test_step_property_value).lower()
        )
        implements_test_step = ".//property/[@name='test_step']/../.."
        if not self._mediator.junit_xml.findall(implements_test_step):
            raise ZigZagTestLogError('Test found without test_step property')
        else:
            return self._mediator.junit_xml.findall(testcases_with_steps_xpath)


class ZigZagTestLogError(Exception):
    """An Error used by _ZigZagTestLog"""

    def __init__(self, message):
        """An error to raise in the event we cant find the automation content"""
        super(ZigZagTestLogError, self).__init__(message)
