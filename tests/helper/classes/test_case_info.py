# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import re
import uuid
import swagger_client
from random import choice
from datetime import datetime, timedelta
from swagger_client.rest import ApiException
from tests.helper.functions import search_qtest
from tests.helper.classes.jira_requirement import JiraRequirementInfo


# ======================================================================================================================
# Classes
# ======================================================================================================================
class TestCaseInfo(object):
    # Class variables
    # This regex will pull the qTest ID for the 'href' attribute on swagger_client.Link model
    _HREF_ID_REGEX = re.compile(r'/(\d+)$')

    def __init__(self,
                 qtest_api_token,
                 qtest_project_id,
                 qtest_req_module_id,
                 state,
                 name=None,
                 class_name=None,
                 file_path=None,
                 line=None,
                 start=None,
                 duration=None,
                 message=None,
                 short_message=None,
                 jira_tickets=None):
        """Capture or generate test case information to be used in validation of JUnitXML documents.

        Args:
            qtest_api_token (str): The API token for the target qTest project.
            qtest_project_id (int): The target qTest project under test.
            qtest_req_module_id (int): The module ID to use as the parent for Jira requirements in the qTest
                'Requirements' view.
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

        Raises:
            RuntimeError: Invalid value provided for the 'state' argument.
        """

        if state not in ('passed', 'skipped', 'failure', 'error'):
            raise RuntimeError("Invalid value provided for the 'state' argument!")

        self._state = state
        self._qtest_api_token = qtest_api_token
        self._qtest_project_id = qtest_project_id
        self._name = name if name else "test_{}".format(str(uuid.uuid1()))
        self._class_name = class_name if class_name else 'tests.test_default'
        self._file_path = file_path if file_path else 'tests/test_default.py'
        self._line = line if line else 1
        self._duration = duration if duration else choice(range(1, 11))
        self._message = message if message else "Test execution state: {}".format(self._state)
        self._short_message = short_message if short_message else "State: {}".format(self._state)
        self._jira_tickets = jira_tickets if jira_tickets else ["JIRA-{}".format(choice(range(1, 100000)))]

        self._test_steps = []
        self._is_test_step = False
        self._has_test_steps = False
        self._test_id = str(uuid.uuid1())
        self._start_time = start if start else datetime.utcnow()
        self._end_time = self._start_time + timedelta(seconds=self._duration)

        self._qtest_req_module_id = qtest_req_module_id
        self._qtest_requirements = None
        self._qtest_testcase_id = None
        self._qtest_test_run_ids = None
        self._qtest_parent_module_id = None
        self._qtest_root_module_id = None

    @property
    def state(self):
        """The execution state of the test artifact. ('passed', 'skipped', 'failure', 'error')

        Returns:
            str: Execution state of the test artifact. ('passed', 'skipped', 'failure', 'error')
        """

        return self._state

    @state.setter
    def state(self, value):
        """Sets the execution state of the test artifact. ('passed', 'skipped', 'failure', 'error')

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
        """The name of the test artifact.

        Returns:
            str: Test artifact name.
        """

        return self._name

    @name.setter
    def name(self, value):
        """Sets the name of the test artifact.

        Args:
            value (str): A name for the test artifact.
        """

        self._name = value

    @property
    def class_name(self):
        """The 'classname' for the test artifact. (JUnitXML 'testcase' attribute)

        Returns:
            str: Test artifact 'classname' JUnitXML attribute.
        """

        return self._class_name

    @class_name.setter
    def class_name(self, value):
        """Sets the 'classname' for the test artifact. (JUnitXML 'testcase' attribute)

        Args:
            value (str): A 'classname' for the test artifact.
        """

        self._class_name = value

    @property
    def file_path(self):
        """The 'file' for the test artifact which is usually a file path. (JUnitXML 'testcase' attribute)

        Returns:
            str: Test artifact 'file' JUnitXML attribute.
        """

        return self._file_path

    @file_path.setter
    def file_path(self, value):
        """Sets the 'file' for the test artifact which is usually a file path. (JUnitXML 'testcase' attribute)

        Args:
            value (str): A path for the 'file' JUnitXML attribute.
        """

        self._file_path = value

    @property
    def line(self):
        """The 'line' number at which the test artifact can be found in the 'file' path. (JUnitXML 'testcase' attribute)

        Returns:
            int: Test artifact 'line' JUnitXML attribute.
        """

        return self._line

    @property
    def duration(self):
        """The execution duration for the test artifact in seconds.

        Returns:
            int: Execution duration for the test artifact in seconds.
        """

        return self._duration

    @property
    def short_msg(self):
        """The short message for non-passed test artifact states.

        Returns:
            int: Short message.
        """

        return self._short_message

    @property
    def long_msg(self):
        """The long message for non-passed test artifact states.

        Returns:
            int: Long message.
        """

        return self._message

    @property
    def jira_tickets(self):
        """A list of 'jira' properties for the test artifact which represent associated Jira tickets.

        Returns:
            list: A list of 'jira' properties for the test artifact.
        """

        return self._jira_tickets

    @property
    def test_id(self):
        """The 'test_id' property for the test artifact.

        Returns:
            str:  Test artifact 'test_id' property.
        """

        return self._test_id

    @property
    def is_test_step(self):
        """Boolean flag indicating if this test artifact is a test step.

        Returns:
            bool
        """

        return self._is_test_step

    @property
    def has_test_steps(self):
        """Boolean flag indicating if this test artifact contains test steps.

        Returns:
            bool
        """

        return self._has_test_steps

    @property
    def start_time(self):
        """The 'start_time' property for the test artifact.

        Returns:
            str: Test artifact 'start_time' property. (In UTC format in Zulu timezone.)
        """

        return self._start_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    @property
    def end_time(self):
        """The 'start_time' property for the test artifact.

        Returns:
            str: Test artifact 'start_time' property. (In UTC format in Zulu timezone.)
        """

        return self._end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    @property
    def test_steps(self):
        """A list of test steps for this test case.

        Returns:
            list
        """

        return self._test_steps

    @property
    def qtest_api_token(self):
        """The qTest API token associated with this test artifact.

        Returns:
            str
        """

        return self._qtest_api_token

    @property
    def qtest_project_id(self):
        """The qTest project ID associated with this test artifact.

        Returns:
            int
        """

        return self._qtest_project_id

    @property
    def qtest_req_module_id(self):
        """The module ID to use as the parent for Jira requirements in the qTest 'Requirements' view.

        Returns:
            int
        """

        return self._qtest_req_module_id

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
            [swagger_client.TestRunWithCustomFieldResource)]

        Raises:
            AssertionError: Associated test runs do not exist.
            RuntimeError: General qTest API failure.
        """

        if not self._qtest_test_run_ids:
            self.assert_executed()

        test_run_api = swagger_client.TestrunApi()

        try:
            return [test_run_api.get(self._qtest_project_id, tr_id, expand='testcase.teststep')
                    for tr_id in self._qtest_test_run_ids]
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))

    @property
    def qtest_requirements(self):
        """A list of qTest swagger_client requirement models associated with the given test case.

        Returns:
            [swagger_client.RequirementResource]

        Raises:
            AssertionError: Associated test runs do not exist.
            RuntimeError: General qTest API failure.
        """

        if not self._qtest_requirements:
            self.assert_requirements_exist()

        try:
            return [req.qtest_req_info for req in self._qtest_requirements]
        except (RuntimeError, AssertionError):
            raise

    @property
    def qtest_parent_test_cycles(self):
        """A list of qTest swagger_client test cycle models which are the direct ancestor for all associated test runs.

        Returns:
            [swagger_client.TestCycleResource]

        Raises:
            AssertionError: Associated test cycles do not exist.
            RuntimeError: General qTest API failure.
        """

        test_cycle_ids = []

        for run in self.qtest_test_runs:
            for link in run.links:
                if link.rel == 'test-cycle':
                    try:
                        test_cycle_ids.append(int(self._HREF_ID_REGEX.search(link.href).group(1)))
                    except (AttributeError, IndexError):
                        raise AssertionError('Test case does not have parent test cycles!')

        test_cycle_api = swagger_client.TestcycleApi()

        try:
            return [test_cycle_api.get_test_cycle(self._qtest_project_id, tc_id) for tc_id in test_cycle_ids]
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))

    def add_test_step(self, state, name=None, line=None, duration=None, message=None, short_message=None):
        """Add a test step to this test case.

        Args:
            state (str): The state of the test. (Valid values: 'passed', 'skipped', 'failure', 'error')
            name (str): The desired name of the test step. (Automatically generated if value is None)
            line (int): The line number at which the test case can be found in the "file_path".
                (Automatically generated if value is None)
            duration (int): The desired duration of the test in seconds. (Automatically generated if value is None)
            message (str): The desired message for the test which is only used for 'skipped', 'failure', 'error'
                test states. (Automatically generated if value is None)
            short_message (str): The desired short message for the test which is only used for 'skipped', 'failure',
                'error' test states. (Automatically generated if value is None)

        Raises:
            AssertionError: Test run does not exist.
        """

        self._end_time = self._start_time if not self._has_test_steps else self._end_time

        try:
            test_step = TestStepInfo(self, state, name, line, self._end_time, duration, message, short_message)
        except RuntimeError:
            raise

        self._test_steps.append(test_step)
        self._duration = self._duration + test_step.duration if self._has_test_steps else test_step.duration
        self._end_time = self._start_time + timedelta(seconds=self._duration)
        self._has_test_steps = True

    def assert_exists(self):
        """Verify that the given test case is present in the "Test Design" view.

        Raises:
            AssertionError: Test case does not exist.
        """

        query = "'Automation Content' ~ '{}'".format(self.test_id)
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

    def assert_requirements_exist(self):
        """Verify qTest requirement resources exist matching the given test case's specified Jira tickets.

        Raises:
            AssertionError: A requirement does not exist.
        """

        if not self._qtest_requirements:
            self._qtest_requirements = []
            for jira_ticket in self._jira_tickets:
                req = JiraRequirementInfo(self._qtest_api_token,
                                          self._qtest_project_id,
                                          self._qtest_req_module_id,
                                          jira_ticket)
                req.assert_exists()
                self._qtest_requirements.append(req)

    def assert_requirements_linked(self):
        """Verify that the given test case is properly linked to all specified Jira requirements in qTest.

        Raises:
            AssertionError: A requirement does not exist or is not linked.
        """

        self.assert_requirements_exist()

        for requirement in self._qtest_requirements:
            requirement.assert_linked(self._qtest_testcase_id)

    def reset(self):
        """Reset cached data on this test case."""

        self._qtest_testcase_id = None
        self._qtest_test_run_ids = None
        self._qtest_parent_module_id = None
        self._qtest_root_module_id = None
        self._qtest_requirements = None

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
            self.reset()

        self.clean_up_requirements()

    def clean_up_requirements(self):
        """Delete all existing requirements associated with this test case.

        Raises:
            RuntimeError: Failed to clean-up or general qTest API failure.
        """

        if self._qtest_requirements:
            for req in self._qtest_requirements:
                req.clean_up()


class TestStepInfo(TestCaseInfo):
    def __init__(self,
                 test_case,
                 state,
                 name=None,
                 line=None,
                 start=None,
                 duration=None,
                 message=None,
                 short_message=None):
        """Capture or generate test case information to be used in validation of JUnitXML documents.

        Args:
            test_case (tests.helper.classes.test_case_info.TestCaseInfo): The parent test case for this step.
            state (str): The state of the test. (Valid values: 'passed', 'skipped', 'failure', 'error')
            name (str): The desired name of the test step. (Automatically generated if value is None)
            line (int): The line number at which the test case can be found in the "file_path".
                (Automatically generated if value is None)
            start (datetime.datetime): Execution start time. (Automatically generated if value is None)
            duration (int): The desired duration of the test in seconds. (Automatically generated if value is None)
            message (str): The desired message for the test which is only used for 'skipped', 'failure', 'error'
                test states. (Automatically generated if value is None)
            short_message (str): The desired short message for the test which is only used for 'skipped', 'failure',
                'error' test states. (Automatically generated if value is None)

        Raises:
            RuntimeError: Invalid value provided for the 'state' argument.
        """

        super(TestStepInfo, self).__init__(test_case.qtest_api_token,
                                           test_case.qtest_project_id,
                                           test_case.qtest_req_module_id,
                                           state,
                                           name if name else "test_step_{}".format(str(uuid.uuid1())),
                                           test_case.class_name,
                                           test_case.file_path,
                                           line,
                                           start,
                                           duration,
                                           message,
                                           short_message,
                                           test_case.jira_tickets)

        self._parent_test_case_info = test_case
        self._test_id = self._parent_test_case_info.test_id
        self._class_name = '{}.{}'.format(self._class_name, test_case.name)
        self._is_test_step = True

    def assert_exists(self):
        """Verify that the given test step and parent test case are present in the "Test Design" view.

        Raises:
            AssertionError: Test case does not exist.
        """

        self._parent_test_case_info.assert_exists()
        self._qtest_testcase_id = self._parent_test_case_info.qtest_test_case_id

        testcase_api = swagger_client.TestcaseApi()

        try:
            test_case = testcase_api.get_test_case(self._qtest_project_id, self.qtest_test_case_id, expand='teststep')
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))

        # Convert the test case to dict and search the description of test steps looking for name of this step.
        assert self.name in [test_step['description'] for test_step in test_case.to_dict()['test_steps']]

    def assert_executed(self):
        """Verify that the given test step and parent test case have been executed at least once.

        Raises:
            AssertionError: Test run does not exist.
        """

        self._parent_test_case_info.assert_executed()
        self._qtest_test_run_ids = self._parent_test_case_info._qtest_test_run_ids

    def reset(self):
        """Reset cached data on this test case."""

        self._parent_test_case_info.reset()

    def clean_up(self):
        """Delete the parent test case and associated test runs from the qTest project under test for this step.

        Use this method with caution as it will only delete the test case and associated runs. It will NOT move the
        "Test Design" module hierarchy or "Test Execution" test cycle hierarchy. Use the "clean_up" method on the
        TestSuiteInfo as a first preference given it can clean-up everything.

        Raises:
            RuntimeError: Failed to clean-up.
            RuntimeError: General qTest API failure.
        """

        self._parent_test_case_info.clean_up()
