# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import uuid
import swagger_client
from datetime import datetime, timedelta
from swagger_client.rest import ApiException
from future.moves.collections import Sequence
from tests.helper.classes.test_case_info import TestCaseInfo


# ======================================================================================================================
# Classes
# ======================================================================================================================
class TestSuiteInfo(Sequence):
    def __init__(self, qtest_api_token, qtest_project_id, qtest_req_module_id):
        """Create a collection of TestCaseInfo objects to be used in validation of JUnitXML documents.

        Args:
            qtest_api_token (str): The API token for the target qTest project.
            qtest_project_id (int): The target qTest project under test.
            qtest_req_module_id (int): The module to use as the parent for Jira requirements in the qTest
                'Requirements' view.
        """

        self._qtest_api_token = qtest_api_token
        self._qtest_project_id = qtest_project_id
        self._qtest_req_module_id = qtest_req_module_id
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
        """The total number of test cases with 'failure' state in this collection.

        Returns:
            int:  The total number of test cases with 'failure' state in this collection.
        """

        return self._failure_count

    @property
    def error_count(self):
        """The total number of test cases with 'error' state in this collection.

        Returns:
            int:  The total number of test cases with 'error' state in this collection.
        """

        return self._error_count

    @property
    def total_duration(self):
        """The total duration for all tests in this collection.

        Returns:
            int:  The total duration for all tests in this collection.
        """

        return self._total_duration

    def add_test_case_info(self, test_case_info):
        """Add an instantiated TestCaseInfo object to the suite.

        Note: This method is meant for complex test scenarios. It is suggested to use "add_test_case" if possible and
        only use this method as a last resort.

        Args:
            test_case_info (tests.helper.classes.test_case_info.TestCaseInfo): Test case to add to this suite.
        """

        if test_case_info.has_test_steps:
            for test_step in test_case_info.test_steps:
                self._tests.append(test_step)
                self._update_test_suite_attributes(test_step)
        else:
            self._tests.append(test_case_info)
            self._update_test_suite_attributes(test_case_info)

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
            short_message (str): The desired short message for the test which is only used for 'skipped', 'failure',
                'error' test states. (Automatically generated if value is None)
            jira_tickets (list): A list of Jira ticket IDs to associated with the test case.
                (Automatically generated if value is None)
            test_steps (list): A list of dictionaries containing keyword arguments for instantiating a TestStepInfo
                object. (See tests.helper.classes.test_step_info._TestStepInfo for details)

        Raises:
            RuntimeError: Invalid value provided for the 'state' argument.
        """

        start = start if start else self._start_time + timedelta(seconds=self._total_duration)

        try:
            test_case = TestCaseInfo(self._qtest_api_token,
                                     self._qtest_project_id,
                                     self._qtest_req_module_id,
                                     state,
                                     name,
                                     class_name,
                                     file_path,
                                     line,
                                     start,
                                     duration,
                                     message,
                                     short_message,
                                     jira_tickets)

            if test_steps:
                # Rewrite the test case name if test steps are included and the caller did not specify a name.
                test_case.name = '{}{}'.format('Test', str(uuid.uuid1()).replace('-', '')) if not name else name
                for test_step in test_steps:
                    test_case.add_test_step(**test_step)
        except RuntimeError:
            raise

        self.add_test_case_info(test_case)

    def assert_requirements_exist(self):
        """Verify qTest requirement resources exist for all tests in this suite.

        Raises:
            AssertionError: A requirement does not exist.
        """

        for test in self._tests:
            test.assert_requirements_exist()

    def assert_requirements_linked(self):
        """Verify that the given test case is properly linked to all specified Jira requirements in qTest.

        Raises:
            AssertionError: A requirement does not exist or is not linked.
        """

        for test in self._tests:
            test.assert_requirements_linked()

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

    def clean_up_requirements(self):
        """Delete all existing requirements associated with tests cases within this suite.

        Raises:
            RuntimeError: Failed to clean-up or general qTest API failure.
        """

        for test in self._tests:
            test.clean_up_requirements()

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

    def _update_test_suite_attributes(self, test_artifact):
        """Update test suite attributes used to render a proper JUnitXML document.

        Args:
            test_artifact (tests.helper.classes.test_artifact_info._TestArtifactInfo): Test artifact from which to
                extract information for updates to the test suite attributes.
        """

        if test_artifact.state == 'skipped':
            self._skip_count += 1
        elif test_artifact.state == 'failure':
            self._failure_count += 1
        elif test_artifact.state == 'error':
            self._error_count += 1

        self._total_count += 1
        self._total_duration += test_artifact.duration

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
