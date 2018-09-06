# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import os
import re
import swagger_client
from time import sleep
from copy import deepcopy
from warnings import warn
from zigzag.zigzag import ZigZag
from swagger_client.rest import ApiException
from jinja2 import Environment, FileSystemLoader
from tests.helper.classes.test_suite_info import TestSuiteInfo

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
                                 "MOLECULE_GIT_COMMIT": "Unknown",
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
                                  "GIT_URL": "Unknown",
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
class ZigZagRunner(object):
    # Class variables
    _queue_job_id_regex = re.compile(r'Queue Job ID: (\d+)')
    _template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'data'))
    _jinja2_env = Environment(loader=FileSystemLoader(_template_dir),
                              trim_blocks=True,
                              lstrip_blocks=True,
                              keep_trailing_newline=True)
    _junit_template = _jinja2_env.get_template('junit.xml.j2')

    def __init__(self,
                 qtest_api_token,
                 qtest_project_id,
                 qtest_root_test_cycle,
                 qtest_root_req_module,
                 junit_xml_file_path,
                 ci_environment,
                 metadata=None):
        """Instantiate an object used to write ZigZag compliant JUnitXML files and execute ZigZag.

        Args:
            qtest_api_token (str): The API token for the target qTest project.
            qtest_project_id (int): The target qTest project to use for publishing results.
            qtest_root_test_cycle (swagger_client.TestCycleResource): The test cycle to use as root for the test results
                hierarchy.
            qtest_root_req_module (swagger_client.ModuleResource): The module to use as the parent for Jira requirements
                in the qTest 'Requirements' view.
            junit_xml_file_path (str): A file path to a JUnitXML file.
            ci_environment (str): The CI environment used to produce the JUnitXML file.
                (Valid values: 'asc', 'mk8s')
            metadata (dict): Provide a dictionary of arbitrary metadata for this runner. Useful for when you want to
                attach extra fixture data to the runner.

        Raises:
            RuntimeError: Invalid value provided for the 'ci_environment' argument.
        """

        if ci_environment == 'asc':
            self._global_props = deepcopy(DEFAULT_ASC_GLOBAL_PROPERTIES)
        elif ci_environment == 'mk8s':
            self._global_props = deepcopy(DEFAULT_MK8S_GLOBAL_PROPERTIES)
        else:
            raise RuntimeError("Invalid value provided for the 'ci_environment' argument!")

        self._ci_environment = ci_environment
        self._qtest_api_token = qtest_api_token
        self._qtest_project_id = qtest_project_id
        self._qtest_root_test_cycle = qtest_root_test_cycle
        self._qtest_root_req_module = qtest_root_req_module
        self._junit_xml_file_path = junit_xml_file_path
        self._metadata = metadata if metadata else {}

        self._last_invocation_queue_job_id = None   # Also used to indicate if runner has ran before
        self._tests = TestSuiteInfo(self.qtest_api_token, self._qtest_project_id, self._qtest_root_req_module.id)
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
    def qtest_project_id(self):
        """The ID for the qTest project used for publishing results.

        Returns:
            int: The target qTest project to use for publishing results.
        """

        return self._qtest_project_id

    @property
    def qtest_root_test_cycle(self):
        """Test cycle information used as root for the test results hierarchy.

        Returns:
            swagger_client.TestCycleResource: The test cycle to use as root for the test results hierarchy.
        """

        return self._qtest_root_test_cycle

    @property
    def qtest_root_req_module(self):
        """Module information used as root for requirements.

        Returns:
            swagger_client.ModuleResource: The module to use as root for the requirements.
        """

        return self._qtest_root_req_module

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
            {str: obj}: Global properties for the test suite.
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

    @property
    def metadata(self):
        """A dictionary of arbitrary metadata for this runner. Useful for when you want to attach extra fixture data
        to the runner.

        Returns:
            dict
        """

        return self._metadata

    def add_test_case_info(self, test_case_info):
        """Add an instantiated TestCaseInfo object to the suite.

        Note: This method is meant for complex test scenarios. It is suggested to use "add_test_case" if possible and
        only use this method as a last resort.

        Args:
            test_case_info (tests.helper.classes.test_case_info.TestCaseInfo): Test case to add to this suite.
        """

        self._tests.add_test_case_info(test_case_info)

    def add_test_case(self,
                      state,
                      name=None,
                      class_name=None,
                      file_path=None,
                      line=None,
                      start=None,
                      duration=None,
                      message=None,
                      short_message=None,
                      jira_tickets=None,
                      test_steps=None):
        """Add a test case to the suite.

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
            short_message (str): The desired short message for the test which is only used for 'skipped', 'failure',
                'error' test states. (Automatically generated if value is None)
            jira_tickets (list): A list of Jira ticket IDs to associated with the test case.
                (Automatically generated if value is None)
            test_steps (list): A list of dictionaries containing keyword arguments for instantiating a TestStepInfo
                object. (See tests.helper.classes.test_step_info._TestStepInfo for details)

        Raises:
            RuntimeError: Invalid value provided for the 'state' argument.
        """

        self._tests.add_test_case(state,
                                  name,
                                  class_name,
                                  file_path,
                                  line,
                                  start,
                                  duration,
                                  message,
                                  short_message,
                                  jira_tickets,
                                  test_steps)

    def invoke_zigzag(self, force_clean_up=True):
        """Execute the ZigZag CLI.

        Args:
            force_clean_up (bool): Flag indicating whether previous test data should be cleaned up first before
                execution. (Default: True)

        """

        if force_clean_up:
            self.clean_up()
        self.tests.reset()  # This is for super safety in case a developer was being tricky with execution

        with open(self._junit_xml_file_path, 'w') as f:
            f.write(self._junit_template.render(tests=self._tests, global_props=self._global_props))

        zz = ZigZag(self._junit_xml_file_path,
                    self._qtest_api_token,
                    self._qtest_project_id,
                    self._qtest_root_test_cycle.name,
                    False)
        zz.parse()

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
                for test_cycle in self.qtest_root_test_cycle.test_cycles:
                    test_cycle_api.delete_cycle(project_id=self.qtest_project_id,
                                                test_cycle_id=test_cycle.id,
                                                force=True)
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
        queue_job_timeout = True

        for i in range(1, 11):
            try:
                response = queue_api.track(self.last_invocation_queue_job_id)

                if response.state == 'SUCCESS':
                    queue_job_timeout = False
                    break
                elif response.state == 'FAILED':
                    raise AssertionError(
                        "Processing for queue job '{}' failed!".format(str(self.last_invocation_queue_job_id))
                    )
                else:
                    warn(UserWarning("WARNING! Queue job retry: #{}".format(str(i))))
                    sleep(3 * i)
            except ApiException as e:
                raise AssertionError("The qTest API reported an error!\n"
                                     "Status code: {}\n"
                                     "Reason: {}\n"
                                     "Message: {}".format(e.status, e.reason, e.body))

        assert not queue_job_timeout, 'Timeout while waiting for queue job to complete!'

    def assert_tests(self):
        """Verify that the test cases exist along with associate test runs.

        Raises:
            AssertionError: Test case or test run doesn't exist or has incorrect attributes.
        """

        for test in self.tests:
            test.assert_exists()
            test.assert_executed()

    def assert_invoke_zigzag(self, force_clean_up=True):
        """Execute the ZigZag CLI and validates if the results were published correctly to qTest.

        Args:
            force_clean_up (bool): Flag indicating whether previous test data should be cleaned up first before
                execution. (Default: True)

        Returns:
            click.testing.Result: Information about the zigzag execution.

        Raises:
            AssertionError: ZigZag invocation failed to publish results correctly.
        """

        self.invoke_zigzag(force_clean_up)
        self.assert_queue_job_complete()
        self.assert_tests()
