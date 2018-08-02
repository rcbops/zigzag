# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import os
import re
import uuid
import json
import pytest
import string
import requests
import swagger_client
from time import sleep
from random import choice
from zigzag.zigzag import ZigZag
from datetime import datetime, timedelta
from swagger_client.rest import ApiException
from jinja2 import Environment, FileSystemLoader
try:
    # noinspection PyCompatibility
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence
pytest_plugins = ['helpers_namespace']

# ======================================================================================================================
# Globals
# ======================================================================================================================
DEFAULT_ASC_GLOBAL_PROPERTIES = {"BUILD_URL": "BUILD_URL",
                                 "BUILD_NUMBER": "BUILD_NUMBER",
                                 "RE_JOB_ACTION": "RE_JOB_ACTION",
                                 "RE_JOB_IMAGE": "RE_JOB_IMAGE",
                                 "RE_JOB_SCENARIO": "RE_JOB_SCENARIO",
                                 "RE_JOB_BRANCH": "pike-rc",
                                 "RPC_RELEASE": "RPC_RELEASE",
                                 "RPC_PRODUCT_RELEASE": "RPC_PRODUCT_RELEASE",
                                 "OS_ARTIFACT_SHA": "OS_ARTIFACT_SHA",
                                 "PYTHON_ARTIFACT_SHA": "PYTHON_ARTIFACT_SHA",
                                 "APT_ARTIFACT_SHA": "APT_ARTIFACT_SHA",
                                 "REPO_URL": "https://github.com/rcbops/rpc-openstack",
                                 "JOB_NAME": "JOB_NAME",
                                 "MOLECULE_TEST_REPO": "MOLECULE_TEST_REPO",
                                 "MOLECULE_SCENARIO_NAME": "MOLECULE_SCENARIO_NAME",
                                 "ci-environment": "asc"}

DEFAULT_MK8S_GLOBAL_PROPERTIES = {"BUILD_URL": "BUILD_URL",
                                  "BUILD_NUMBER": "BUILD_NUMBER",
                                  "BUILD_ID": "BUILD_ID",
                                  "JOB_NAME": "JOB_NAME",
                                  "BUILD_TAG": "BUILD_TAG",
                                  "JENKINS_URL": "JENKINS_URL",
                                  "EXECUTOR_NUMBER": "EXECUTOR_NUMBER",
                                  "WORKSPACE": "WORKSPACE",
                                  "CVS_BRANCH": "CVS_BRANCH",
                                  "GIT_COMMIT": "GIT_COMMIT",
                                  "GIT_URL": "https://github.com/rcbops/mk8s.git",
                                  "GIT_BRANCH": "master",
                                  "GIT_LOCAL_BRANCH": "GIT_LOCAL_BRANCH",
                                  "GIT_AUTHOR_NAME": "GIT_AUTHOR_NAME",
                                  "GIT_AUTHOR_EMAIL": "GIT_AUTHOR_EMAIL",
                                  "BRANCH_NAME": "BRANCH_NAME",
                                  "CHANGE_AUTHOR_DISPLAY_NAME": "CHANGE_AUTHOR_DISPLAY_NAME",
                                  "CHANGE_AUTHOR": "CHANGE_AUTHOR",
                                  "CHANGE_BRANCH": "CHANGE_BRANCH",
                                  "CHANGE_FORK": "CHANGE_FORK",
                                  "CHANGE_ID": "CHANGE_ID",
                                  "CHANGE_TARGET": "CHANGE_TARGET",
                                  "CHANGE_TITLE": "CHANGE_TITLE",
                                  "CHANGE_URL": "CHANGE_URL",
                                  "JOB_URL": "JOB_URL",
                                  "NODE_LABELS": "NODE_LABELS",
                                  "NODE_NAME": "NODE_NAME",
                                  "PWD": "PWD",
                                  "STAGE_NAME": "STAGE_NAME",
                                  "ci-environment": "mk8s"}


# ======================================================================================================================
# Classes
# ======================================================================================================================
class TestCaseInfo(object):
    def __init__(self,
                 qtest_api_token,
                 qtest_project_id,
                 state,
                 name=None,
                 class_name=None,
                 file_path=None,
                 line=None,
                 start=None,
                 duration=None,
                 message=None,
                 jira_tickets=None):
        """Capture or generate test case information to be used in validation of JUnitXML documents.

        Args:
            qtest_api_token (str): The API token for the target qTest project.
            qtest_project_id (int): The target qTest project under test.
            state (str): The state of the test. (Valid values: 'passed', 'skipped', 'failure', 'error')
            name (str): The desired name of the test. (Automatically generated if value is None)
            class_name (str): The desired classname of the test. (Automatically generated if value is None)
            file_path (str): The desired file path of the test. (Automatically generated if value is None)
            line (int): The line number at which the test case can be found in the "file_path".
                (Automatically generated if value is None)
            start (datetime.datetime): Execution start time. (Automatically generated if value is None)
            duration (int): The desired duration of the test in seconds. (Automatically generated if value is None)
            message (str): The desired message for the test which is only used for 'skipped', 'failure', 'error'
                test states. (Automatically generated if value is None)
            jira_tickets (list(str)): A list of Jira ticket IDs to associated with the test case.
                (Automatically generated if value is None)

        Raises:
            RuntimeError: Invalid value provided for the 'state' argument.
        """

        if state not in ('passed', 'skipped', 'failure', 'error'):
            raise RuntimeError("Invalid value provided for the 'state' argument!")

        self._state = state
        self._qtest_api_token = qtest_api_token
        self._qtest_project_id = qtest_project_id
        self._name = name if name else "test_{}".format(str(uuid.uuid1()))
        self._class_name = class_name
        self._file_path = file_path
        self._line = line
        self._duration = duration if duration else 1
        self._message = message if message else "Test execution state: {}".format(self._state)
        self._jira_tickets = jira_tickets if jira_tickets \
            else ["JIRA-{}".format(''.join(choice(string.digits) for _ in range(4)))]

        self._test_id = str(uuid.uuid1())
        self._start_time = start if start else datetime.utcnow()
        self._end_time = self._start_time + timedelta(seconds=self._duration)
        self._qtest_testcase_id = None
        self._qtest_test_run_ids = None
        self._qtest_parent_module_id = None
        self._qtest_root_module_id = None

    @property
    def state(self):
        """The execution state of the test case. ('passed', 'skipped', 'failure', 'error')

        Returns:
            str: Execution state of the test case. ('passed', 'skipped', 'failure', 'error')
        """

        return self._state

    @state.setter
    def state(self, value):
        """Sets the execution state of the test case. ('passed', 'skipped', 'failure', 'error')

        Args:
            value (str): A valid state. ('passed', 'skipped', 'failure', 'error')

        Raises:
            RuntimeError: Invalid state provided for the 'value' argument.
        """

        if value not in ('passed', 'skipped', 'failure', 'error'):
            raise RuntimeError("Invalid state provided for the 'value' argument!")

        self._state = value

    @property
    def name(self):
        """The name of the test case.

        Returns:
            str: Test case name.
        """

        return self._name

    @property
    def class_name(self):
        """The 'classname' for the test case. (JUnitXML 'testcase' attribute)

        Returns:
            str: Test case 'classname' JUnitXML attribute.
        """

        return self._class_name

    @property
    def file_path(self):
        """The 'file' for the test case which is usually a file path. (JUnitXML 'testcase' attribute)

        Returns:
            str: Test case 'file' JUnitXML attribute.
        """

        return self._file_path

    @property
    def line(self):
        """The 'line' number at which the test case can be found in the 'file' path. (JUnitXML 'testcase' attribute)

        Returns:
            int: Test case 'line' JUnitXML attribute.
        """

        return self._line

    @property
    def duration(self):
        """The execution duration for the test case in seconds.

        Returns:
            int: Execution duration for the test case in seconds.
        """

        return self._duration

    @property
    def short_msg(self):
        """The short message for non-passed test case states.

        Returns:
            int: Short message.
        """

        return "{} (short)".format(self._message)

    @property
    def long_msg(self):
        """The long message for non-passed test case states.

        Returns:
            int: Long message.
        """

        return "{} (long)".format(self._message)

    @property
    def jira_tickets(self):
        """A list of 'jira' properties for the test case which represent associated Jira tickets.

        Returns:
            str: A list of 'jira' properties for the test case.
        """

        return self._jira_tickets

    @property
    def test_id(self):
        """The 'test_id' property for the test case.

        Returns:
            str:  Test case 'test_id' property.
        """

        return self._test_id

    @property
    def start_time(self):
        """The 'start_time' property for the test case.

        Returns:
            str: Test case 'start_time' property. (In UTC format in Zulu timezone.)
        """

        return self._start_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    @property
    def end_time(self):
        """The 'start_time' property for the test case.

        Returns:
            str: Test case 'start_time' property. (In UTC format in Zulu timezone.)
        """

        return self._end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    @property
    def qtest_parent_module_id(self):
        """The qTest parent module ID for the given test case.

        Returns:
            int: The qTest parent module ID for the given test case.

        Raises:
            AssertionError: Test case does not exist.
            RuntimeError: General qTest API failure.
        """

        if not self._qtest_parent_module_id:
            testcase_api = swagger_client.TestcaseApi()

            try:
                self._qtest_parent_module_id = \
                    testcase_api.get_test_case(self._qtest_project_id, self.qtest_test_case_id).parent_id
            except ApiException as e:
                raise RuntimeError("The qTest API reported an error!\n"
                                   "Status code: {}\n"
                                   "Reason: {}\n"
                                   "Message: {}".format(e.status, e.reason, e.body))

        return self._qtest_parent_module_id

    @property
    def qtest_root_module_id(self):
        """The qTest root module ID of the "Test Design" module hierarchy for the given test case.

        Returns:
            int: The qTest parent module ID for the given test case. (Returns 0 if test case already cleaned-up or
                reset)

        Raises:
            RuntimeError: General qTest API failure.
        """

        if self._qtest_testcase_id:
            def _find_root_module(module_id, last_id=None):
                module_api = swagger_client.ModuleApi()

                try:
                    parent_module_id = module_api.get_module(self._qtest_project_id, module_id).parent_id
                except ApiException as e:
                    if e.status == 404 and 'Module does not exist' in e.body:
                        parent_module_id = None
                    else:
                        raise RuntimeError("The qTest API reported an error!\n"
                                           "Status code: {}\n"
                                           "Reason: {}\n"
                                           "Message: {}".format(e.status, e.reason, e.body))

                if parent_module_id:
                    return _find_root_module(parent_module_id, last_id=module_id)
                else:
                    return last_id

            if not self._qtest_root_module_id:
                self._qtest_root_module_id = _find_root_module(self.qtest_parent_module_id)

            return self._qtest_root_module_id
        else:
            return 0

    @property
    def qtest_test_case_id(self):
        """The qTest test case ID for the given test case.

        Returns:
            int: The qTest test case ID for the given test case.

        Raises:
            AssertionError: Test case does not exist.
        """

        if not self._qtest_testcase_id:
            self.assert_exists()

        return self._qtest_testcase_id

    @property
    def qtest_test_case_info(self):
        """The qTest swagger_client model with detailed information for the given test case.

        Returns:
            swagger_client.TestCaseWithCustomFieldResource

        Raises:
            AssertionError: Test case does not exist.
            RuntimeError: General qTest API failure.
        """

        if not self._qtest_testcase_id:
            self.assert_exists()

        testcase_api = swagger_client.TestcaseApi()

        try:
            return testcase_api.get_test_case(self._qtest_project_id, self.qtest_test_case_id)
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))

    @property
    def qtest_test_runs(self):
        """A list of qTest swagger_client detailed test run models associated with the given test case.

        Returns:
            list(swagger_client.TestRunWithCustomFieldResource)

        Raises:
            AssertionError: Associated test runs do not exist.
            RuntimeError: General qTest API failure.
        """

        if not self._qtest_test_run_ids:
            self.assert_executed()

        test_run_api = swagger_client.TestrunApi()

        try:
            return [test_run_api.get(self._qtest_project_id, tr_id) for tr_id in self._qtest_test_run_ids]
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))

    def clean_up(self):
        """Delete the test case and associated test runs from the qTest project under test.

        Use this method with caution as it will only delete the test case and associated runs. It will NOT move the
        "Test Design" module hierarchy or "Test Execution" test cycle hierarchy. Use the "clean_up" method on the
        TestSuiteInfo as a first preference given it can clean-up everything.

        Raises:
            RuntimeError: Failed to clean-up.
            RuntimeError: General qTest API failure.
        """

        if self._qtest_testcase_id:
            testcase_api = swagger_client.TestcaseApi()

            try:
                testcase_api.delete_test_case(self._qtest_project_id, self.qtest_test_case_id)
            except ApiException as e:
                raise RuntimeError("The qTest API reported an error!\n"
                                   "Status code: {}\n"
                                   "Reason: {}\n"
                                   "Message: {}".format(e.status, e.reason, e.body))

    def assert_exists(self):
        """Verify that the given test case is present in the "Test Design" view.

        Raises:
            AssertionError: Test case does not exist.
        """

        query = "'name' ~ '{}'".format(self.name)
        result = search_qtest(self._qtest_api_token, self._qtest_project_id, 'test-cases', query, ['id'])

        if result['items']:
            self._qtest_testcase_id = result['items'][0]['id']
        else:
            raise AssertionError("Test case '{}' does not exist!".format(self.name))

    def assert_executed(self):
        """Verify that the given test case has been executed at least once.

        Raises:
            AssertionError: Test run does not exist.
        """

        query = "'name' ~ '{}'".format(self.name)
        result = search_qtest(self._qtest_api_token, self._qtest_project_id, 'test-runs', query, ['id'])

        if result['items']:
            self._qtest_test_run_ids = [test_run['id'] for test_run in result['items']]
        else:
            raise AssertionError("Test case '{}' has no associate test runs!".format(self.name))

    def reset(self):
        """Reset cached data on this test case."""

        self._qtest_testcase_id = None
        self._qtest_test_run_ids = None
        self._qtest_parent_module_id = None
        self._qtest_root_module_id = None


class TestSuiteInfo(Sequence):
    def __init__(self, qtest_api_token, qtest_project_id):
        """Create a collection of TestCaseInfo objects to be used in validation of JUnitXML documents.

        Args:
            qtest_api_token (str): The API token for the target qTest project.
            qtest_project_id (int): The target qTest project under test.
        """

        self._qtest_api_token = qtest_api_token
        self._qtest_project_id = qtest_project_id
        self._tests = []
        self._total_count = 0
        self._skip_count = 0
        self._failure_count = 0
        self._error_count = 0
        self._total_duration = 0
        self._start_time = datetime.utcnow()

    @property
    def total_count(self):
        """The total number of test cases in this collection.

        Returns:
            int:  The total number of test cases in this collection.
        """

        return self._total_count

    @property
    def skip_count(self):
        """The total number of test cases with 'skipped' state in this collection.

        Returns:
            int:  The total number of test cases with 'skipped' state in this collection.
        """

        return self._skip_count

    @property
    def failure_count(self):
        """The total number of test cases with 'failed' state in this collection.

        Returns:
            int:  The total number of test cases with 'failed' state in this collection.
        """

        return self._failure_count

    @property
    def error_count(self):
        """The total number of test cases with 'errored' state in this collection.

        Returns:
            int:  The total number of test cases with 'errored' state in this collection.
        """

        return self._error_count

    @property
    def total_duration(self):
        """The total duration for all tests in this collection.

        Returns:
            int:  The total duration for all tests in this collection.
        """

        return self._total_duration

    def add_test_case(self,
                      state,
                      name=None,
                      class_name=None,
                      file_path=None,
                      line=None,
                      start=None,
                      duration=None,
                      message=None,
                      jira_tickets=None):
        """Add a test case to the collection of test cases.

        Args:
            state (str): The state of the test. (Valid values: 'passed', 'skipped', 'failure', 'error')
            name (str): The desired name of the test. (Automatically generated if value is None)
            class_name (str): The desired classname of the test. (Automatically generated if value is None)
            file_path (str): The desired file path of the test. (Automatically generated if value is None)
            line (int): The line number at which the test case can be found in the "file_path".
                (Automatically generated if value is None)
            start (datetime.datetime): Execution start time. (Automatically generated if value is None)
            duration (int): The desired duration of the test in seconds. (Automatically generated if value is None)
            message (str): The desired message for the test which is only used for 'skipped', 'failure', 'error'
                test states. (Automatically generated if value is None)
            jira_tickets (list(str)): A list of Jira ticket IDs to associated with the test case.
                (Automatically generated if value is None)

        Raises:
            RuntimeError: Invalid value provided for the 'state' argument.
        """

        start = start if start else self._start_time
        duration = duration if duration else choice(range(1, 11))

        try:
            test_case = TestCaseInfo(self._qtest_api_token,
                                     self._qtest_project_id,
                                     state,
                                     name,
                                     class_name,
                                     file_path,
                                     line,
                                     start,
                                     duration,
                                     message,
                                     jira_tickets)
        except RuntimeError:
            raise

        self._tests.append(test_case)

        if test_case.state == 'skipped':
            self._skip_count += 1
        elif test_case.state == 'failed':
            self._failure_count += 1
        elif test_case.state == 'errored':
            self._error_count += 1

        self._total_count += 1
        self._total_duration += duration
        self._start_time = self._start_time + timedelta(duration)

    def clean_up(self, clean_up_modules=False):
        """Delete all test cases and optionally the test module hierarchy if "clean_up_modules" is enabled.

        Args:
            clean_up_modules (bool): Clean-up the module hierarchy in the qTest "Test Design" view. (Default is False)

        Raises:
            RuntimeError: Failed to clean-up.
        """

        root_module_ids = []
        module_api = swagger_client.ModuleApi()

        if clean_up_modules:
            for test in self._tests:
                if test.qtest_root_module_id not in root_module_ids:
                    root_module_ids.append(test.qtest_root_module_id)

            for root_module_id in [rmid for rmid in root_module_ids if rmid != 0]:
                try:
                    module_api.delete_module(self._qtest_project_id, root_module_id, force=True)
                except ApiException as e:
                    if not (e.status == 404 and 'Module does not exist' in e.body):
                        raise RuntimeError("The qTest API reported an error!\n"
                                           "Status code: {}\n"
                                           "Reason: {}\n"
                                           "Message: {}".format(e.status, e.reason, e.body))
        else:
            for test in self._tests:
                test.clean_up()

    def count(self, value):
        """Return the number of times x appears in the list.

        Args:
            value (object): Desired value to search for within the list.

        Returns:
            int: number of times 'value' appears in the list.
        """

        return self._tests.count(value)

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

        return self._tests.index(value, start, stop)

    def reset(self):
        """Reset cached data for all the tests in this suite."""

        for test in self._tests:
            test.reset()

    def __reversed__(self):
        """Sequence ABC override."""

        return self._tests.__reversed__()

    def __contains__(self, item):
        """Sequence ABC override."""

        return self._tests.__contains__(item)

    def __getitem__(self, key):
        """Sequence ABC override."""

        return self._tests.__getitem__(key)

    def __iter__(self):
        """Sequence ABC override."""

        return iter(self._tests)

    def __len__(self):
        """Sequence ABC override."""

        return len(self._tests)


class ZigZagRunner(object):
    # Class variables
    _queue_job_id_regex = re.compile(r'Queue Job ID: (\d+)')
    _template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    _jinja2_env = Environment(loader=FileSystemLoader(_template_dir),
                              trim_blocks=True,
                              lstrip_blocks=True,
                              keep_trailing_newline=True)
    _junit_template = _jinja2_env.get_template('junit.xml.j2')

    def __init__(self, qtest_api_token, project_id, root_test_cycle, junit_xml_file_path, ci_environment):
        """Instantiate an object used to write ZigZag compliant JUnitXML files and execute ZigZag.

        Args:
            qtest_api_token (str): The API token for the target qTest project.
            project_id (int): The target qTest project to use for publishing results.
            root_test_cycle (swagger_client.TestCycleResource): The test cycle to use as root for the test results
                hierarchy.
            junit_xml_file_path (str): A file path to a JUnitXML file.
            ci_environment (str): The CI environment used to produce the JUnitXML file.
                (Valid values: 'asc', 'mk8s')

        Raises:
            RuntimeError: Invalid value provided for the 'ci_environment' argument.
        """

        if ci_environment == 'asc':
            self._global_props = DEFAULT_ASC_GLOBAL_PROPERTIES
        elif ci_environment == 'mk8s':
            self._global_props = DEFAULT_MK8S_GLOBAL_PROPERTIES
        else:
            raise RuntimeError("Invalid value provided for the 'ci_environment' argument!")

        self._ci_environment = ci_environment
        self._qtest_api_token = qtest_api_token
        self._project_id = project_id
        self._root_test_cycle = root_test_cycle
        self._junit_xml_file_path = junit_xml_file_path

        self._last_invocation_queue_job_id = None   # Also used to indicate if runner has ran before
        self._tests = TestSuiteInfo(self.qtest_api_token, self.project_id)
        self._last_line = 0
        self._last_time = 1

    @property
    def qtest_api_token(self):
        """The API token for the target qTest project.

        Returns:
            str: The API token for the target qTest project.
        """

        return self._qtest_api_token

    @property
    def project_id(self):
        """The ID for the qTest project used for publishing results.

        Returns:
            int: The target qTest project to use for publishing results.
        """

        return self._project_id

    @property
    def root_test_cycle(self):
        """Test cycle information used as root for the test results hierarchy.

        Returns:
            swagger_client.TestCycleResource: The test cycle to use as root for the test results hierarchy.
        """

        return self._root_test_cycle

    @property
    def junit_xml_file_path(self):
        """A file path to a JUnitXML file.

        Returns:
            str: A file path to a JUnitXML file.
        """

        return self._junit_xml_file_path

    @property
    def ci_environment(self):
        """The CI environment used to produce the JUnitXML file.

        Returns:
            str: The CI environment used to produce the JUnitXML file.
        """

        return self._ci_environment

    @property
    def global_props(self):
        """The global properties for the test suite.

        Returns:
            dict(str): Global properties for the test suite.
        """

        return self._global_props

    @property
    def tests(self):
        """The tests associated with this runner.

        Returns:
            TestSuiteInfo: The tests associated with this runner.
        """

        return self._tests

    @property
    def last_invocation_queue_job_id(self):
        """The queue job ID for the last call to "invoke_zigzag".

        Returns:
            int: The queue job ID for the last call to "invoke_zigzag".

        Raises:
            AssertionError: The "invoke_zigzag" has not been called yet.
        """

        assert self._last_invocation_queue_job_id
        return self._last_invocation_queue_job_id

    def add_test_case(self,
                      state,
                      name=None,
                      class_name=None,
                      file_path=None,
                      line=None,
                      start=None,
                      duration=None,
                      message=None,
                      jira_tickets=None):
        """Add a test case to the collection of test cases.

        Args:
            state (str): The state of the test. (Valid values: 'passed', 'skipped', 'failure', 'error')
            name (str): The desired name of the test. (Automatically generated if value is None)
            class_name (str): The desired classname of the test. (Automatically generated if value is None)
            file_path (str): The desired file path of the test. (Automatically generated if value is None)
            line (int): The line number at which the test case can be found in the "file_path".
                (Automatically generated if value is None)
            start (datetime.datetime): Execution start time. (Automatically generated if value is None)
            duration (int): The desired duration of the test in seconds. (Automatically generated if value is None)
            message (str): The desired message for the test which is only used for 'skipped', 'failure', 'error'
                test states. (Automatically generated if value is None)
            jira_tickets (list(str)): A list of Jira ticket IDs to associated with the test case.
                (Automatically generated if value is None)

        Raises:
            RuntimeError: Invalid value provided for the 'state' argument.
        """

        self._tests.add_test_case(state, name, class_name, file_path, line, start, duration, message, jira_tickets)

    def invoke_zigzag(self, force_clean_up=True):
        """Execute the ZigZag CLI.

        Args:
            force_clean_up (bool): Flag indicating whether previous test data should be cleaned up first before
                execution. (Default: True)

        """

        if force_clean_up:
            self.clean_up()
        self.tests.reset()  # This is for super safety in case a developer was being tricky with execution

        with open(self._junit_xml_file_path, 'wb') as f:
            f.write(self._junit_template.render(tests=self._tests, global_props=self._global_props))

        zz = ZigZag(self._junit_xml_file_path,
                    self._qtest_api_token,
                    self._project_id,
                    self._root_test_cycle.name,
                    False)

        self._last_invocation_queue_job_id = zz.upload_test_results()

    def clean_up(self):
        """Remove qTest elements from the "Test Design" and "Test Execution" views.

        Raises:
            RuntimeError: Failed to cleanup all qTest elements.
        """

        if self._last_invocation_queue_job_id:
            test_cycle_api = swagger_client.TestcycleApi()

            self.tests.clean_up()

            try:
                for test_cycle in self.root_test_cycle.test_cycles:
                    test_cycle_api.delete_cycle(project_id=self.project_id, test_cycle_id=test_cycle.id, force=True)
            except ApiException as e:
                raise RuntimeError("The qTest API reported an error!\n"
                                   "Status code: {}\n"
                                   "Reason: {}\n"
                                   "Message: {}".format(e.status, e.reason, e.body))

            self._last_invocation_queue_job_id = None

    def assert_queue_job_complete(self):
        """Verify that the queue job for the last call to "invoke_zigzag" completed successfully.

        Raises:
            AssertionError: Queue job failed or timeout while waiting for job to complete.
        """

        queue_api = swagger_client.TestlogApi()

        for i in range(10):
            try:
                response = queue_api.track(self.last_invocation_queue_job_id)

                if response.state == 'SUCCESS':
                    break
                elif response.state == 'FAILED':
                    raise AssertionError(
                        "Processing for queue job '{}' failed!".format(str(self.last_invocation_queue_job_id))
                    )
                else:
                    sleep(3 * i)
            except ApiException as e:
                raise AssertionError("The qTest API reported an error!\n"
                                     "Status code: {}\n"
                                     "Reason: {}\n"
                                     "Message: {}".format(e.status, e.reason, e.body))

    def assert_tests(self):
        """Verify that the test cases exist along with associate test runs.

        Raises:
            AssertionError: Test case or test run doesn't exist or has incorrect attributes.
        """

        for test in self.tests:
            test.assert_exists()
            test.assert_executed()

    def assert_invoke_zigzag(self):
        """Execute the ZigZag CLI and validates if the results were published correctly to qTest.

        Returns:
            click.testing.Result: Information about the zigzag execution.

        Raises:
            AssertionError: ZigZag invocation failed to publish results correctly.
        """

        self.invoke_zigzag()
        self.assert_queue_job_complete()
        self.assert_tests()


# ======================================================================================================================
# Helpers
# ======================================================================================================================
# noinspection PyUnresolvedReferences
@pytest.helpers.register
def search_qtest(qtest_api_token, qtest_project_id, object_type, query, fields=None):
    """Search qTest for objects matching a given query. (This helper exists because the swagger_client search API
    returns a really useless model)

    Args:
        qtest_api_token (str): The API token for the target qTest project.
        qtest_project_id (int): The target qTest project to use for publishing results.
        object_type (str): The type of qTest objects to search.
            (Valid values: 'requirements', 'test-cases', 'test-runs', 'defects')
        query (str): The query to execute against the given object type.
        fields (list(str)): A list of qTest object field names to capture in the return data.
            (All fields captured if None is specified)

    Returns:
        dict: A dictionary representing the JSON return data from the endpoint.

    Raises:
        RuntimeError: qTest API request failed.
    """

    fields = fields if fields else ['*']
    headers = {'Authorization': qtest_api_token, 'Content-Type': 'application/json'}
    endpoint = \
        "https://apitryout.qtestnet.com/api/v3/projects/{}/search?pageSize=100&page=1".format(str(qtest_project_id))

    body = {'object_type': object_type,
            'fields': fields,
            'query': "{}".format(query)}

    try:
        r = requests.post(endpoint, data=json.dumps(body), headers=headers)
        r.raise_for_status()
        parsed = json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise RuntimeError("The qTest API reported an error!\n"
                           "Status code: {}\n"
                           "Reason: {}\n"
                           "Message: {}".format(e.status, e.reason, e.body))

    return parsed


# noinspection PyUnresolvedReferences
@pytest.helpers.register
def get_qtest_property(model, prop_name):
    """Get the value for a qTest swagger_client model property. This helper will intelligently search both standard
    qTest swagger_client model attributes as well as custom fields set by the qTest admin of the qTest project under
    test.

    Enabling 'promiscuous' mode (default) will attempt to retrieve the property value against either the 'field_value'
    or 'field_value_name' attributes of the model. If 'promiscuous' mode is disabled then retrieval of the expected
    property value will only be made against the 'field_value' attribute of the model.

    Args:
        model (object): Any model from the 'swagger_client.models' namespace.
        prop_name (str): Target property name to use for value validation.

    Returns:
        [obj]: list of values for desired property. Data type could be anything depending on what the model specifies.
            Also, multiple values will be returned if the requested property is a custom qTest field.

    Raises:
        AssertionError: Property name does not exist.
    """

    actual_values = []
    model_dict = model.to_dict()
    try:
        custom_props = {p['field_name']: (p['field_value'], p['field_value_name']) for p in model_dict['properties']}
    except KeyError:
        custom_props = {}

    if prop_name in model_dict:
        actual_values.append(model[prop_name])
    elif prop_name in custom_props:
        actual_values = custom_props[prop_name]
    else:
        raise AssertionError("The '{}' property not found in the provided swagger_client model!".format(prop_name))

    return actual_values


# noinspection PyUnresolvedReferences
@pytest.helpers.register
def assert_qtest_property(model, prop_name, exp_prop_value, promiscuous=True):
    """Assert that a qTest swagger_client model has a property that matches the expected value. This assert will
    intelligently search both standard qTest swagger_client model attributes as well as custom fields set by the
    qTest admin of the qTest project under test.

    Enabling 'promiscuous' mode (default) will attempt to match the property value against either the 'field_value' or
    'field_value_name' attributes of the model. If 'promiscuous' mode is disabled then validation of the expected
    property value will only be made against the 'field_value' attribute of the model.

    Args:
        model (object): Any model from the 'swagger_client.models' namespace.
        prop_name (str): Target property name to use for value validation.
        exp_prop_value (str): Expected value for the given property name.
        promiscuous (bool): Flag for indicating whether to run assertion in 'promiscuous' mode or not. (See above)

    Raises:
        AssertionError: Property name does not exist or property value does not match expected value.
    """

    actual_values = get_qtest_property(model, prop_name)

    if promiscuous:
        assert exp_prop_value in actual_values
    else:
        assert actual_values[0] == exp_prop_value


# noinspection PyUnresolvedReferences
@pytest.helpers.register
def assert_qtest_property_match(model, prop_name, exp_prop_regex, regex_flags=0, promiscuous=True):
    """Assert that a qTest swagger_client model has a property that matches a given regular expression. This assert will
    intelligently search both standard qTest swagger_client model attributes as well as custom fields set by the
    qTest admin of the qTest project under test.

    NOTE: Regex is run in 'match' mode with this helper!

    Enabling 'promiscuous' mode (default) will attempt to match the property value against either the 'field_value' or
    'field_value_name' attributes of the model. If 'promiscuous' mode is disabled then validation of the expected
    property value will only be made against the 'field_value' attribute of the model.

    Args:
        model (object): Any model from the 'swagger_client.models' namespace.
        prop_name (str): Target property name to use for value validation.
        exp_prop_regex (str): Regular expression pattern that property value is expected to match.
        regex_flags (int): Flags to pass to the regex evaluator to alter pattern matching behavior.
        promiscuous (bool): Flag for indicating whether to run assertion in 'promiscuous' mode or not. (See above)

    Raises:
        AssertionError: Property name does not exist or property value failed regular expression match.
    """

    actual_values = get_qtest_property(model, prop_name)

    if promiscuous:
        assert any([re.match(exp_prop_regex, value, regex_flags) for value in actual_values if type(value) is str])
    else:
        assert re.match(exp_prop_regex, actual_values[0], regex_flags)


# noinspection PyUnresolvedReferences
@pytest.helpers.register
def assert_qtest_property_search(model, prop_name, exp_prop_regex, regex_flags=0, promiscuous=True):
    """Assert that a qTest swagger_client model has a property that matches a given regular expression. This assert will
    intelligently search both standard qTest swagger_client model attributes as well as custom fields set by the
    qTest admin of the qTest project under test.

    NOTE: Regex is run in 'search' mode with this helper!

    Enabling 'promiscuous' mode (default) will attempt to match the property value against either the 'field_value' or
    'field_value_name' attributes of the model. If 'promiscuous' mode is disabled then validation of the expected
    property value will only be made against the 'field_value' attribute of the model.

    Args:
        model (object): Any model from the 'swagger_client.models' namespace.
        prop_name (str): Target property name to use for value validation.
        exp_prop_regex (str): Regular expression pattern that property value is expected to match.
        regex_flags (int): Flags to pass to the regex evaluator to alter pattern matching behavior.
        promiscuous (bool): Flag for indicating whether to run assertion in 'promiscuous' mode or not. (See above)

    Raises:
        AssertionError: Property name does not exist or property value failed regular expression match.
    """

    actual_values = get_qtest_property(model, prop_name)

    if promiscuous:
        assert any([re.search(exp_prop_regex, value, regex_flags) for value in actual_values if type(value) is str])
    else:
        assert re.search(exp_prop_regex, actual_values[0], regex_flags)


# ======================================================================================================================
# Private Fixtures: Meant to be consumed by other fixtures
# ======================================================================================================================
# noinspection PyShadowingNames
@pytest.fixture(scope='session')
def _configure_test_environment(qtest_env_vars):
    """Configure the qTest project for testing.

    Returns:
        swagger_client.TestCycleResource: Test cycle information.

    Raises:
        RuntimeError: Failed to create or cleanup all qTest elements.
    """

    # Setup
    swagger_client.configuration.api_key['Authorization'] = qtest_env_vars['QTEST_API_TOKEN']
    project_id = qtest_env_vars['QTEST_SANDBOX_PROJECT_ID']
    test_cycle_api = swagger_client.TestcycleApi()

    try:
        test_cycle = test_cycle_api.create_cycle(
            project_id=project_id,
            parent_id=0,
            parent_type='root',
            body=swagger_client.TestCycleResource(name=str(uuid.uuid1())))
    except ApiException as e:
        raise RuntimeError("The qTest API reported an error!\n"
                           "Status code: {}\n"
                           "Reason: {}\n"
                           "Message: {}".format(e.status, e.reason, e.body))

    yield test_cycle

    # Teardown
    try:
        test_cycle_api.delete_cycle(project_id=project_id, test_cycle_id=test_cycle.id, force=True)
    except ApiException as e:
        raise RuntimeError("The qTest API reported an error!\n"
                           "Status code: {}\n"
                           "Reason: {}\n"
                           "Message: {}".format(e.status, e.reason, e.body))


# noinspection PyShadowingNames
@pytest.fixture(scope='session')
def _zigzag_runner_factory(qtest_env_vars, _configure_test_environment, tmpdir_factory):
    """Instantiate an objects used to write ZigZag compliant JUnitXML files and execute ZigZag CLI.

    Returns:
        ZigZagRunner: Write ZigZag compliant JUnitXML files and execute ZigZag CLI.
    """

    zz_runners = []
    root_module_ids = []
    temp_dir = tmpdir_factory.mktemp('data')

    def _factory(junit_xml_file_name, ci_environment):
        """Instantiate an object used to write ZigZag compliant JUnitXML files and execute ZigZag CLI.

        Args:
            junit_xml_file_name (str): The name of the JUnitXML file. (Do not supply a file path!)
            ci_environment (str): The CI environment used to produce the JUnitXML file.

        Returns:
            ZigZagRunner: Write ZigZag compliant JUnitXML files and execute ZigZag CLI.

        Raises:
            RuntimeError: Invalid value provided for the 'ci_environment' argument.
        """

        junit_xml_file_path = temp_dir.join(junit_xml_file_name).strpath
        runner = ZigZagRunner(qtest_env_vars['QTEST_API_TOKEN'],
                              qtest_env_vars['QTEST_SANDBOX_PROJECT_ID'],
                              _configure_test_environment,
                              junit_xml_file_path,
                              ci_environment)
        zz_runners.append(runner)

        return runner

    yield _factory

    # Teardown
    module_api = swagger_client.ModuleApi()

    for zz_runner in zz_runners:
        for test in zz_runner.tests:
            if (test.qtest_root_module_id != 0) and (test.qtest_root_module_id not in root_module_ids):
                root_module_ids.append(test.qtest_root_module_id)

    for root_module_id in root_module_ids:
        try:
            module_api.delete_module(qtest_env_vars['QTEST_SANDBOX_PROJECT_ID'], root_module_id, force=True)
        except ApiException as e:
            if not (e.status == 404 and 'Module does not exist' in e.body):
                raise RuntimeError("The qTest API reported an error!\n"
                                   "Status code: {}\n"
                                   "Reason: {}\n"
                                   "Message: {}".format(e.status, e.reason, e.body))


# ======================================================================================================================
# Public Fixtures: Meant to be consumed by tests
# ======================================================================================================================
@pytest.fixture(scope='session')
def qtest_env_vars():
    """Retrieve a dictionary of required environment variables for running integration tests.

    Returns:
        dict(str): A dictionary of environment variables. (Case sensitive)
    """

    env_vars = {}

    # noinspection PyUnusedLocal
    __tracebackhide__ = True
    try:
        env_vars['QTEST_API_TOKEN'] = os.environ['QTEST_API_TOKEN']
        env_vars['QTEST_SANDBOX_PROJECT_ID'] = int(os.environ['QTEST_SANDBOX_PROJECT_ID'])
    except KeyError:
        raise pytest.fail('Necessary environment variables not present!')

    return env_vars


@pytest.fixture(scope='session')
def single_passing_test_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with one passing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_passing_asc.xml', 'asc')
    zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def single_passing_test_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with one passing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_passing_mk8s.xml', 'mk8s')
    zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def single_failing_test_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with one failing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_failing_asc.xml', 'asc')
    zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def single_failing_test_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with one failing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_failing_mk8s.xml', 'mk8s')
    zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_passing_tests_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 passing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_passing_asc.xml', 'asc')
    for i in range(3):
        zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_passing_tests_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 passing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_passing_mk8s.xml', 'mk8s')
    for i in range(3):
        zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_failing_tests_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 failing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_failing_asc.xml', 'asc')
    for i in range(3):
        zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_failing_tests_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 failing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_failing_mk8s.xml', 'mk8s')
    for i in range(3):
        zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_erroring_tests_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 erroring tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_erroring_asc.xml', 'asc')
    for i in range(3):
        zz_runner.add_test_case('error')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_erroring_tests_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 erroring tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_erroring_mk8s.xml', 'mk8s')
    for i in range(3):
        zz_runner.add_test_case('error')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_skipping_tests_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 skipping tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_skipping_asc.xml', 'asc')
    for i in range(3):
        zz_runner.add_test_case('skipped')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_skipping_tests_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 skipping tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_skipping_mk8s.xml', 'mk8s')
    for i in range(3):
        zz_runner.add_test_case('skipped')

    return zz_runner


@pytest.fixture(scope='session')
def mixed_status_tests_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with 4 tests covering the various test execution
     states in the JUnitXML file

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_mixed_asc.xml', 'asc')
    for state in ('passed', 'failure', 'error', 'skipped'):
        zz_runner.add_test_case(state)

    return zz_runner


@pytest.fixture(scope='session')
def mixed_status_tests_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 4 tests covering the various test execution
     states in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_mixed_mk8s.xml', 'mk8s')
    for state in ('passed', 'failure', 'error', 'skipped'):
        zz_runner.add_test_case(state)

    return zz_runner
