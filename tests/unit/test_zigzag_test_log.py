# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import json
import pytest
import requests
import swagger_client
from zigzag.zigzag import ZigZag
from zigzag.zigzag_test_log import ZigZagTestLogs


# ======================================================================================================================
# Globals
# ======================================================================================================================
TOKEN = 'VALID_TOKEN'
PROJECT_ID = 12345
TEST_CYCLE = 'CL-1'
LONG_FAILURE_MESSAGE = ('This is a very long failure message produced by a test fixture in order to validate that the '
                        'failure output truncation works as intended because clowns!')
DEFAULT_SEARCH_RESPONSE = {
    "links": [],
    "page": 1,
    "page_size": 100,
    "total": 1,
    "items": [
        {
            "id": 5678,
            "name": "PRO-18405 Fake!"
        }
    ]
}


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
@pytest.fixture
def mock_zigzag(mocker):
    """A mock patcher for ZigZag invocations. (Sane defaults)"""

    def _factory(search_response=None):
        search_response = DEFAULT_SEARCH_RESPONSE if not search_response else search_response
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)

        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        return mocker

    return _factory


@pytest.fixture(scope='module')
def short_single_line_failure_message(tmpdir_factory, default_global_properties, default_testcase_properties):
    """Failing test case with a short single line failure message."""

    filename = tmpdir_factory.mktemp('data').join('short_single_line_failure_message.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                {testcase_properties}
                <failure message="short">Short</failure>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties, testcase_properties=default_testcase_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def long_single_line_failure_message(tmpdir_factory, default_global_properties, default_testcase_properties):
    """Failing test case with a long (153 characters) single line failure message."""

    filename = tmpdir_factory.mktemp('data').join('long_single_line_failure_message.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                {testcase_properties}
                <failure message="long">{failure_message}</failure>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   failure_message=LONG_FAILURE_MESSAGE)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def long_multi_line_failure_message(tmpdir_factory, default_global_properties, default_testcase_properties):
    """Failing test case with 7 long (153 characters) lines in failure message."""

    filename = tmpdir_factory.mktemp('data').join('long_multi_line_failure_message.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                {testcase_properties}
                <failure message="very long">
                    {failure_message}
                    {failure_message}
                    {failure_message}
                    {failure_message}
                    {failure_message}
                    {failure_message}
                    {failure_message}
                </failure>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   failure_message=LONG_FAILURE_MESSAGE)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_test_with_mixed_status_steps_xml(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing a single test case with multiple steps."""

    test_step_testcase_properties = \
        """
                    <properties>
                        <property name="jira" value="ASC-123"/>
                        <property name="test_id" value="1"/>
                        <property name="test_step" value="true"/>
                        <property name="start_time" value="2018-04-10T21:38:18Z"/>
                        <property name="end_time" value="2018-04-10T21:38:19Z"/>
                    </properties>
        """

    filename = tmpdir_factory.mktemp('data').join('single_test_with_mixed_status_steps.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
            <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="8"
            name="test_step_pass[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="12"
            name="test_step_fail[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
            </testcase>
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="15"
            name="test_step_skip[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=test_step_testcase_properties,
                   testcase_name='TestCaseWithSteps')

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_test_with_multiple_skipping_steps_xml(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing a single test case with multiple skipping steps."""

    test_step_testcase_properties = \
        """
                    <properties>
                        <property name="jira" value="ASC-123"/>
                        <property name="test_id" value="1"/>
                        <property name="test_step" value="true"/>
                        <property name="start_time" value="2018-04-10T21:38:18Z"/>
                        <property name="end_time" value="2018-04-10T21:38:19Z"/>
                    </properties>
        """

    filename = tmpdir_factory.mktemp('data').join('single_test_with_multiple_skipping_steps.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
            <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="15"
            name="test_skip_step[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
            </testcase>
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="15"
            name="test_skip_step[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=test_step_testcase_properties,
                   testcase_name='TestCaseWithSteps')

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_test_with_multiple_passing_steps_xml(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing a single test case with multiple passing steps."""

    test_step_testcase_properties = \
        """
                    <properties>
                        <property name="jira" value="ASC-123"/>
                        <property name="test_id" value="1"/>
                        <property name="test_step" value="true"/>
                        <property name="start_time" value="2018-04-10T21:38:18Z"/>
                        <property name="end_time" value="2018-04-10T21:38:19Z"/>
                    </properties>
        """

    filename = tmpdir_factory.mktemp('data').join('single_test_with_multiple_passing_steps.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
            <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="15"
            name="test_pass_step[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="15"
            name="test_pass_step[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=test_step_testcase_properties,
                   testcase_name='TestCaseWithSteps')

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def multiple_mixed_status_tests_with_step_xml(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing multiple test cases with various statuses along with a single step each."""

    test_step_testcase_properties = \
        """
                    <properties>
                        <property name="jira" value="ASC-123"/>
                        <property name="test_id" value="1"/>
                        <property name="test_step" value="true"/>
                        <property name="start_time" value="2018-04-10T21:38:18Z"/>
                        <property name="end_time" value="2018-04-10T21:38:19Z"/>
                    </properties>
        """

    filename = tmpdir_factory.mktemp('data').join('multiple_mixed_status_tests_with_step.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
            <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default.TestCasePass" file="tests/test_default.py" line="8"
            name="test_step_pass[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default.TestCaseFail" file="tests/test_default.py" line="12"
            name="test_step_fail[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
            </testcase>
            <testcase classname="tests.test_default.TestCaseSkip" file="tests/test_default.py" line="15"
            name="test_step_skip[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties, testcase_properties=test_step_testcase_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def multiple_mixed_status_tests_with_steps_xml(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing multiple test cases with various statuses along with multiple steps each."""

    test_step_testcase_properties = \
        """
                    <properties>
                        <property name="jira" value="ASC-123"/>
                        <property name="test_id" value="1"/>
                        <property name="test_step" value="true"/>
                        <property name="start_time" value="2018-04-10T21:38:18Z"/>
                        <property name="end_time" value="2018-04-10T21:38:19Z"/>
                    </properties>
        """

    filename = tmpdir_factory.mktemp('data').join('multiple_mixed_status_tests_steps.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
            <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default.TestCasePass" file="tests/test_default.py" line="8"
            name="test_pass_step_0[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default.TestCasePass" file="tests/test_default.py" line="8"
            name="test_pass_step_1[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default.TestCaseFail" file="tests/test_default.py" line="12"
            name="test_fail_step_0[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
            </testcase>
            <testcase classname="tests.test_default.TestCaseFail" file="tests/test_default.py" line="12"
            name="test_fail_step_1[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
            </testcase>
            <testcase classname="tests.test_default.TestCaseSkip" file="tests/test_default.py" line="15"
            name="test_skip_step_0[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
            </testcase>
            <testcase classname="tests.test_default.TestCaseSkip" file="tests/test_default.py" line="15"
            name="test_skip_step_1[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties, testcase_properties=test_step_testcase_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def multiple_tests_with_and_without_steps_xml(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing a mix of test cases with and without steps."""

    filename = tmpdir_factory.mktemp('data').join('multiple_tests_with_and_without_steps.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
            <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default.TestCaseWithSteps" file="tests/test_default.py" line="8"
            name="test_step[ansible://localhost]" time="0.00372695922852">
                <properties>
                    <property name="jira" value="ASC-123"/>
                    <property name="test_id" value="1"/>
                    <property name="test_step" value="true"/>
                    <property name="start_time" value="2018-04-10T21:38:18Z"/>
                    <property name="end_time" value="2018-04-10T21:38:19Z"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_case_without_steps[ansible://localhost]" time="0.00372695922852">
                <properties>
                    <property name="jira" value="ASC-123"/>
                    <property name="test_id" value="1"/>
                    <property name="test_step" value="false"/>
                    <property name="start_time" value="2018-04-10T21:38:18Z"/>
                    <property name="end_time" value="2018-04-10T21:38:19Z"/>
                </properties>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
# noinspection PyProtectedMember
class TestZigZagTestLog(object):
    """Tests for the _ZigZagTestLog class through the ZigZagTestLogs public class."""

    def test_lookup_ids(self, single_passing_xml, mock_zigzag):
        """Test for _lookup_ids happy path"""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Expectations
        qtest_id_exp = 5678

        # Test
        tl = ZigZagTestLogs(zz)[0]   # Create a new TestLog object through the ZigZagTestLogs public class
        assert tl.qtest_testcase_id == qtest_id_exp

    def test_lookup_ids_not_found(self, single_passing_xml, mock_zigzag):
        """Test for _lookup_ids
        Ask for a test ID that does not exist yet
        """

        # Setup
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 0,
            "items": []
        }
        mock_zigzag(search_response)
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]   # Create a new TestLog object through the ZigZagTestLogs public class
        assert tl.qtest_testcase_id is None

    def test_lookup_requirements_not_found(self, single_passing_xml, mock_zigzag):
        """Test for _lookup_requirements
        Ask for a requirements that have not been imported from jira yet
        """

        # Setup
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 0,
            "items": []
        }
        mock_zigzag(search_response)
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]   # Create a new TestLog object through the ZigZagTestLogs public class
        assert isinstance(tl.qtest_requirements, list)
        assert not len(tl.qtest_requirements)

    def test_lookup_requirements(self, single_passing_xml, mock_zigzag):
        """Test for _lookup_requirements
        Ask for two requirements that correspond to jira ids
        """

        # Expectations
        qtest_id_exp = 123456789

        # Setup
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 1,
            "items": [
                {
                    "id": qtest_id_exp,
                    "name": "PRO-18405 Fake!"
                }
            ]
        }
        mock_zigzag(search_response)
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]   # Create a new TestLog object through the ZigZagTestLogs public class
        assert isinstance(tl.qtest_requirements, list)
        # there should be two requirements since xml has two jira marks
        assert tl.qtest_requirements == [qtest_id_exp, qtest_id_exp]

    def test_successful_test_case_attachments(self, single_passing_xml, mock_zigzag):
        """Test to ensure that test artifacts are being correctly attached
        Ensure that there is only one attachment (junit.xml) in the passing case.
        """

        # Setup
        mock_zigzag()
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class

        # there should be a list of two attachments: the junit xml
        # file and a text log
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 1
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'


class TestZigZagTestLogWithSteps(object):
    """Tests for the _ZigZagTestLog class through the ZigZagTestLogs public class."""

    def test_single_test_multiple_steps(self, single_test_with_mixed_status_steps_xml, mock_zigzag):
        """Verify a single test case with multiple test steps is handled correctly."""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_test_with_mixed_status_steps_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Expectations
        test_step_log_exps = \
            [
                {'actual_result': 'PASSED',
                 'description': 'test_step_pass',
                 'expected_result': 'pass',
                 'order': 0,
                 'status': 'PASSED'},
                {'actual_result': ("Log truncated, please see attached failure log for more details..."
                                   "\n            def test_fail(host):\n        >       assert False"
                                   "\n        E       assert False"),
                 'description': 'test_step_fail',
                 'expected_result': 'pass',
                 'order': 1,
                 'status': 'FAILED'},
                {'actual_result': 'SKIPPED',
                 'description': 'test_step_skip',
                 'expected_result': 'pass',
                 'order': 2,
                 'status': 'SKIPPED'},
             ]

        # Test
        test_logs = ZigZagTestLogs(zz)
        assert len(test_logs) == 1
        assert len(test_logs[0].qtest_test_log.test_step_logs) == 3
        assert test_logs[0].name == 'TestCaseWithSteps'
        assert test_logs[0].status == 'FAILED'
        assert test_logs[0].module_hierarchy[-1] == 'test_default'  # Validate that the hierarchy was adjusted.
        for ts_log_actual, ts_log_exp in zip(test_logs[0].qtest_test_log.test_step_logs, test_step_log_exps):
            # noinspection PyUnresolvedReferences
            assert pytest.helpers.is_sub_dict(ts_log_exp, ts_log_actual.to_dict())

    def test_single_test_multiple_skipping_steps(self, single_test_with_multiple_skipping_steps_xml, mock_zigzag):
        """Verify a single test case with multiple test steps is handled correctly."""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_test_with_multiple_skipping_steps_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Expectations
        test_step_log_exp = {'actual_result': 'SKIPPED',
                             'description': 'test_skip_step',
                             'expected_result': 'pass',
                             'status': 'SKIPPED'}

        # Test
        test_logs = ZigZagTestLogs(zz)
        assert len(test_logs) == 1
        assert len(test_logs[0].qtest_test_log.test_step_logs) == 2
        assert test_logs[0].name == 'TestCaseWithSteps'
        assert test_logs[0].status == 'SKIPPED'
        assert test_logs[0].module_hierarchy[-1] == 'test_default'  # Validate that the hierarchy was adjusted.
        for ts_log in test_logs[0].qtest_test_log.test_step_logs:
            # noinspection PyUnresolvedReferences
            assert pytest.helpers.is_sub_dict(test_step_log_exp, ts_log.to_dict())

    def test_single_test_multiple_passing_steps(self, single_test_with_multiple_passing_steps_xml, mock_zigzag):
        """Verify a single test case with multiple test steps is handled correctly."""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_test_with_multiple_passing_steps_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Expectations
        test_step_log_exp = {'actual_result': 'PASSED',
                             'description': 'test_pass_step',
                             'expected_result': 'pass',
                             'status': 'PASSED'}

        # Test
        test_logs = ZigZagTestLogs(zz)
        assert len(test_logs) == 1
        assert len(test_logs[0].qtest_test_log.test_step_logs) == 2
        assert test_logs[0].name == 'TestCaseWithSteps'
        assert test_logs[0].status == 'PASSED'
        assert test_logs[0].module_hierarchy[-1] == 'test_default'  # Validate that the hierarchy was adjusted.
        for ts_log in test_logs[0].qtest_test_log.test_step_logs:
            # noinspection PyUnresolvedReferences
            assert pytest.helpers.is_sub_dict(test_step_log_exp, ts_log.to_dict())

    def test_multiple_tests_with_step(self, multiple_mixed_status_tests_with_step_xml, mock_zigzag):
        """Verify a multiple test case with a single test step each are handled correctly."""

        # Setup
        mock_zigzag()
        zz = ZigZag(multiple_mixed_status_tests_with_step_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Expectations
        tl_details_exps = \
            {
                'TestCasePass': {'actual_result': 'PASSED',
                                 'description': 'test_step_pass',
                                 'expected_result': 'pass',
                                 'status': 'PASSED'},
                'TestCaseFail': {'actual_result': ("Log truncated, please see attached failure log for more details..."
                                                   "\n            def test_fail(host):\n        >       assert False"
                                                   "\n        E       assert False"),
                                 'description': 'test_step_fail',
                                 'expected_result': 'pass',
                                 'status': 'FAILED'},
                'TestCaseSkip': {'actual_result': 'SKIPPED',
                                 'description': 'test_step_skip',
                                 'expected_result': 'pass',
                                 'status': 'SKIPPED'}
            }

        # Test
        tl_details = {tl.name: tl for tl in ZigZagTestLogs(zz)}
        assert tl_details.keys() == tl_details_exps.keys()
        for test_case_name in tl_details_exps:
            assert tl_details[test_case_name].module_hierarchy[-1] == 'test_default'
            assert tl_details[test_case_name].qtest_test_log.status == tl_details_exps[test_case_name]['status']
            # noinspection PyUnresolvedReferences
            assert pytest.helpers.is_sub_dict(tl_details_exps[test_case_name],
                                              tl_details[test_case_name].qtest_test_log.test_step_logs[0].to_dict())

    def test_multiple_tests_with_multiple_steps(self, multiple_mixed_status_tests_with_steps_xml, mock_zigzag):
        """Verify a multiple test cases with multiple test steps are handled correctly."""

        # Setup
        mock_zigzag()
        zz = ZigZag(multiple_mixed_status_tests_with_steps_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Expectations
        tl_details_exps = \
            {
                'TestCasePass': [
                    {'actual_result': 'PASSED',
                     'description': 'test_pass_step_0',
                     'expected_result': 'pass',
                     'status': 'PASSED'},
                    {'actual_result': 'PASSED',
                     'description': 'test_pass_step_1',
                     'expected_result': 'pass',
                     'status': 'PASSED'}
                ],
                'TestCaseFail': [
                    {'actual_result': ("Log truncated, please see attached failure log for more details..."
                                       "\n            def test_fail(host):\n        >       assert False"
                                       "\n        E       assert False"),
                     'description': 'test_fail_step_0',
                     'expected_result': 'pass',
                     'status': 'FAILED'},
                    {'actual_result': ("Log truncated, please see attached failure log for more details..."
                                       "\n            def test_fail(host):\n        >       assert False"
                                       "\n        E       assert False"),
                     'description': 'test_fail_step_1',
                     'expected_result': 'pass',
                     'status': 'FAILED'}
                ],
                'TestCaseSkip': [
                    {'actual_result': 'SKIPPED',
                     'description': 'test_skip_step_0',
                     'expected_result': 'pass',
                     'status': 'SKIPPED'},
                    {'actual_result': 'SKIPPED',
                     'description': 'test_skip_step_1',
                     'expected_result': 'pass',
                     'status': 'SKIPPED'}
                ]
            }

        # Test
        tl_details = {tl.name: tl for tl in ZigZagTestLogs(zz)}
        assert tl_details.keys() == tl_details_exps.keys()
        for test_case_name in tl_details_exps:
            assert tl_details[test_case_name].module_hierarchy[-1] == 'test_default'
            assert tl_details[test_case_name].qtest_test_log.status == tl_details_exps[test_case_name][0]['status']
            assert len(tl_details[test_case_name].qtest_test_log.test_step_logs) == 2
            for test_step, test_step_exp in zip(tl_details[test_case_name].qtest_test_log.test_step_logs,
                                                tl_details_exps[test_case_name]):
                # noinspection PyUnresolvedReferences
                assert pytest.helpers.is_sub_dict(test_step_exp, test_step.to_dict())


class TestZigZagTestLogs(object):
    """Tests for the TestLog class"""

    def test_mix_of_test_logs(self, multiple_tests_with_and_without_steps_xml, mock_zigzag):
        """Verify that a test suite with a mix of tests with and without steps is handled correctly."""

        # Setup
        mock_zigzag()
        zz = ZigZag(multiple_tests_with_and_without_steps_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Expectations
        ts_detail_exp = {'actual_result': 'PASSED',
                         'description': 'test_step',
                         'expected_result': 'pass',
                         'status': 'PASSED'}

        # Test
        tls = ZigZagTestLogs(zz)

        assert len(tls) == 2
        assert tls[0].name == 'TestCaseWithSteps'
        assert tls[0].status == 'PASSED'
        assert tls[0].module_hierarchy[-1] == 'test_default'
        # noinspection PyUnresolvedReferences
        assert pytest.helpers.is_sub_dict(ts_detail_exp, tls[0].qtest_test_log.test_step_logs[0].to_dict())
        assert tls[1].name == 'test_case_without_steps'
        assert tls[1].status == 'PASSED'
        assert tls[0].module_hierarchy[-1] == 'test_default'
        assert tls[1].qtest_test_log.test_step_logs is None


# noinspection PyProtectedMember
class TestFailedTestCases(object):
    """Tests for failure output messagage and failure log attachment."""

    def test_failed_test_case_attachments(self, single_fail_xml, mock_zigzag):
        """Test to ensure that test artifacts are being correctly attached
        Ensure that there are two attachments, one of type xml and one of type
        text.
        """

        # Setup
        mock_zigzag()
        zz = ZigZag(single_fail_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class

        # there should be a list of two attachments: the junit xml
        # file and a text log
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 2
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'
        assert tl.qtest_test_log.attachments[1].content_type == 'text/plain'

    def test_failed_test_step_attachments(self, single_test_with_mixed_status_steps_xml, mock_zigzag):
        """Test to ensure that test artifacts are being correctly attached to test steps upon failure."""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_test_with_mixed_status_steps_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]

        # The test log should have the junit xml file and a failure text log attached.
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 2
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'
        assert tl.qtest_test_log.attachments[1].content_type == 'text/plain'

        # The failing step should have a failure text log attached.
        failing_step = tl.qtest_test_log.test_step_logs[1]      # Failing step at known location.
        assert len(failing_step.attachments) == 1
        assert failing_step.attachments[0].content_type == 'text/plain'

    def test_truncated_failure_output(self, single_fail_xml, mock_zigzag):
        """Test to ensure that log messages are truncated correctly"""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_fail_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class

        assert len(tl._failure_output.split('\n')) == 4

    def test_truncated_failure_output_with_short_single_line_message(self, short_single_line_failure_message,
                                                                     mock_zigzag):
        """Verify that a failure output of only one line will NOT be truncated."""

        # Setup
        mock_zigzag()
        zz = ZigZag(short_single_line_failure_message, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class

        assert tl._failure_output == 'Short'

    def test_truncated_failure_output_with_long_single_line_message(self, long_single_line_failure_message,
                                                                    mock_zigzag):
        """Verify that a failure output of only one line will NOT be truncated."""

        # Setup
        mock_zigzag()
        zz = ZigZag(long_single_line_failure_message, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class

        assert tl._failure_output == LONG_FAILURE_MESSAGE[:120] + '...'

    def test_truncated_failure_output_with_long_multi_line_message(self, long_multi_line_failure_message, mock_zigzag):
        """Verify that a failure output of only one line will NOT be truncated."""

        # Setup
        mock_zigzag()
        zz = ZigZag(long_multi_line_failure_message, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class

        assert len(tl._failure_output.split('\n')) == 4
        assert 'Log truncated' in tl._failure_output
        assert '{}{}'.format(LONG_FAILURE_MESSAGE[:100], '...') in tl._failure_output
