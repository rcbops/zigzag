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
from zigzag.zigzag_test_log import _ZigZagTestLog
from zigzag.zigzag_test_log import _ZigZagTestLogTempest
from zigzag.zigzag_test_log import ZigZagTestLogError
from datetime import datetime
from datetime import timedelta
from uuid import UUID
from lxml import etree


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
def test_execution_parameters(tmpdir_factory, default_global_properties, default_testcase_properties):
    """A single passing test that does not have 'system-out' or 'system-err' testcase elements."""

    filename = tmpdir_factory.mktemp('data').join('single_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_assign_floating_ip_to_instance[_testinfra_host0]" time="0.00372695922852">
                {testcase_properties}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties, testcase_properties=default_testcase_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_passing_no_sys_capture_xml(tmpdir_factory, default_global_properties, default_testcase_properties):
    """A single passing test that does not have 'system-out' or 'system-err' testcase elements."""

    filename = tmpdir_factory.mktemp('data').join('single_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties, testcase_properties=default_testcase_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_failing_no_sys_capture_xml(tmpdir_factory, default_global_properties, default_testcase_properties):
    """A single failing test that does not have 'system-out' or 'system-err' testcase elements."""

    filename = tmpdir_factory.mktemp('data').join('single_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                {testcase_properties}
                <failure message="fail">Fail</failure>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties, testcase_properties=default_testcase_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_failing_duplicate_sys_capture_xml(tmpdir_factory,
                                             default_global_properties,
                                             default_testcase_properties,
                                             default_testcase_elements):
    """A single failing test that has duplicate 'system-out' and 'system-err' testcase elements."""

    filename = tmpdir_factory.mktemp('data').join('single_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                {testcase_properties}
                <failure message="fail">Fail</failure>
                {testcase_elements}
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_failing_missing_sys_err_xml(tmpdir_factory, default_global_properties, default_testcase_properties):
    """A single failing test that does not have 'system-err' testcase element."""

    filename = tmpdir_factory.mktemp('data').join('single_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                {testcase_properties}
                <failure message="fail">Fail</failure>
                <system-out>stdout</system-out>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties, testcase_properties=default_testcase_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_failing_missing_sys_out_xml(tmpdir_factory, default_global_properties, default_testcase_properties):
    """A single failing test that does not have 'system-out' testcase element."""

    filename = tmpdir_factory.mktemp('data').join('single_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                {testcase_properties}
                <failure message="fail">Fail</failure>
                <system-err>stderr</system-err>
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties, testcase_properties=default_testcase_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def short_single_line_failure_message(tmpdir_factory,
                                      default_global_properties,
                                      default_testcase_properties,
                                      default_testcase_elements):
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
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def long_single_line_failure_message(tmpdir_factory,
                                     default_global_properties,
                                     default_testcase_properties,
                                     default_testcase_elements):
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
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   failure_message=LONG_FAILURE_MESSAGE,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def long_multi_line_failure_message(tmpdir_factory,
                                    default_global_properties,
                                    default_testcase_properties,
                                    default_testcase_elements):
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
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   failure_message=LONG_FAILURE_MESSAGE,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_test_with_mixed_status_steps_xml(tmpdir_factory, default_global_properties, default_testcase_elements):
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
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="12"
            name="test_step_fail[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="15"
            name="test_step_skip[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=test_step_testcase_properties,
                   testcase_name='TestCaseWithSteps',
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_test_with_mixed_status_steps_no_sys_capture_xml(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing a single test case with multiple steps. The failing step does not have
    'system-err' or 'system-out' elements.
    """

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
def single_test_with_mixed_status_steps_missing_sys_err_xml(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing a single test case with multiple steps. The failing step does not have
    the 'system-err' element.
    """

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
                <system-out>stdout</system-out>
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
def single_test_with_mixed_status_steps_missing_sys_out_xml(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing a single test case with multiple steps. The failing step does not have
    the 'system-out' element.
    """

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
                <system-err>stderr</system-err>
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
def single_test_with_multiple_skipping_steps_xml(tmpdir_factory, default_global_properties, default_testcase_elements):
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
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="15"
            name="test_skip_step[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=test_step_testcase_properties,
                   testcase_name='TestCaseWithSteps',
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def single_test_with_multiple_passing_steps_xml(tmpdir_factory, default_global_properties, default_testcase_elements):
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
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.{testcase_name}" file="tests/test_default.py" line="15"
            name="test_pass_step[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=test_step_testcase_properties,
                   testcase_name='TestCaseWithSteps',
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def multiple_mixed_status_tests_with_step_xml(tmpdir_factory, default_global_properties, default_testcase_elements):
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
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestCaseFail" file="tests/test_default.py" line="12"
            name="test_step_fail[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestCaseSkip" file="tests/test_default.py" line="15"
            name="test_step_skip[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=test_step_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def multiple_mixed_status_tests_with_steps_xml(tmpdir_factory, default_global_properties, default_testcase_elements):
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
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestCasePass" file="tests/test_default.py" line="8"
            name="test_pass_step_1[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestCaseFail" file="tests/test_default.py" line="12"
            name="test_fail_step_0[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestCaseFail" file="tests/test_default.py" line="12"
            name="test_fail_step_1[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestCaseSkip" file="tests/test_default.py" line="15"
            name="test_skip_step_0[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestCaseSkip" file="tests/test_default.py" line="15"
            name="test_skip_step_1[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=test_step_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def multiple_tests_with_and_without_steps_xml(tmpdir_factory, default_global_properties, default_testcase_elements):
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
                {testcase_elements}
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
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties, testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='module')
def tempest_case_xml_passed():
    """Tempest XML from a passed case"""
    xml = """
    <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_password_history_not_enforced_in_admin_reset[id-568cd46c-ee6c-4ab4-a33a-d3791931979e]" time="0.000"></testcase>
    """  # noqa
    xml = etree.fromstring(xml)

    return xml


@pytest.fixture(scope='module')
def tempest_case_xml_failed():
    """Tempest XML from a failed case"""
    xml = """
    <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_password_history_not_enforced_in_admin_reset[id-568cd46c-ee6c-4ab4-a33a-d3791931979e]" time="0.000">
                <failure>It's a failure yo!</failure>
    </testcase>
    """  # noqa
    xml = etree.fromstring(xml)

    return xml


@pytest.fixture(scope='module')
def tempest_case_xml_error():
    """Tempest XML from a error case"""
    xml = """
    <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_password_history_not_enforced_in_admin_reset[id-568cd46c-ee6c-4ab4-a33a-d3791931979e]" time="0.000">
                <error>Something bad happened here yo!</error>
    </testcase>
    """  # noqa
    xml = etree.fromstring(xml)

    return xml


@pytest.fixture(scope='module')
def tempest_case_xml_skip():
    """Tempest XML from a skipped case"""
    xml = """
    <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_password_history_not_enforced_in_admin_reset[id-568cd46c-ee6c-4ab4-a33a-d3791931979e]" time="0.000">
                <skipped>Security compliance not available.</skipped>
    </testcase>
    """  # noqa
    xml = etree.fromstring(xml)

    return xml


@pytest.fixture(scope='module')
def tempest_case_xml_with_execution_parameters():
    """Tempest XML from a failed case"""
    xml = """
    <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_server_basic_ops[compute,id-7fff3fb3-91d8-4fd0-bd7d-0204f1f180ba,network,smoke]" time="0.000">
                <failed>It's a failure yo!</failed>
    </testcase>
    """  # noqa
    xml = etree.fromstring(xml)

    return xml


@pytest.fixture(scope='module')
def tempest_case_xml_with_empty_exec_params():
    """Tempest XML from a failed case"""
    xml = """
    <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_server_basic_ops[,,,]" time="0.000">
                <failed>It's a failure yo!</failed>
    </testcase>
    """  # noqa
    xml = etree.fromstring(xml)

    return xml


@pytest.fixture(scope='module')
def tempest_xml_with_some_none_exec_params():
    """Tempest XML from a failed case"""
    xml = """
    <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_server_basic_ops[foo,,bar,]" time="0.000">
                <failed>It's a failure yo!</failed>
    </testcase>
    """  # noqa
    xml = etree.fromstring(xml)

    return xml


@pytest.fixture(scope='module')
def tempest_xml_with_no_exec_params():
    """Tempest XML from a failed case"""
    xml = """
    <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_server_basic_ops[]" time="0.000">
                <failed>It's a failure yo!</failed>
    </testcase>
    """  # noqa
    xml = etree.fromstring(xml)

    return xml


@pytest.fixture(scope='module')
def tempest_xml_with_none_for_exec_params():
    """Tempest XML from a failed case"""
    xml = """
    <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_server_basic_ops" time="0.000">
                <failed>It's a failure yo!</failed>
    </testcase>
    """  # noqa
    xml = etree.fromstring(xml)

    return xml


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
# noinspection PyProtectedMember
class TestZigZagTestLog(object):
    """Tests for the _ZigZagTestLog class through the ZigZagTestLogs public class."""

    def test_single_passing_no_sys_capture(self, single_passing_no_sys_capture_xml, mock_zigzag):
        """Test that nothing blows up if the JUnitXML testcase element lacks 'system-out' and 'system-err' elements."""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_passing_no_sys_capture_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Expectations
        qtest_id_exp = 5678

        # Test
        tl = ZigZagTestLogs(zz)[0]   # Create a new TestLog object through the ZigZagTestLogs public class
        assert not tl.stderr
        assert not tl.stdout
        assert tl.qtest_testcase_id == qtest_id_exp

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

    def test_lookup_test_execution_parameters_not_found(self, single_passing_xml, mock_zigzag):
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
        assert tl.test_execution_parameters == ['ansible://localhost']

    def test_lookup_test_execution_parameters_found(self, test_execution_parameters, mock_zigzag):
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
        zz = ZigZag(test_execution_parameters, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]   # Create a new TestLog object through the ZigZagTestLogs public class
        assert tl.test_execution_parameters == ['_testinfra_host0']

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
        assert tl.stderr == 'stderr'
        assert tl.stdout == 'stdout'

        # there should be a list of two attachments: the junit xml
        # file and a text log
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 1
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'

    def test_status_pass(self, single_passing_xml, mocker):
        """Verify the status property when we expect a pass"""

        # Setup
        zz = mocker.MagicMock()
        junit_xml_doc = etree.parse(single_passing_xml)
        junit_xml = junit_xml_doc.getroot()
        xml = junit_xml.find('testcase')

        zztl = _ZigZagTestLog(xml, zz)

        assert 'PASSED' == zztl.status

    def test_status_error(self, single_error_xml, mocker):
        """Verify the status property when we expect a error"""

        # Setup
        zz = mocker.MagicMock()
        junit_xml_doc = etree.parse(single_error_xml)
        junit_xml = junit_xml_doc.getroot()
        xml = junit_xml.find('testcase')

        zztl = _ZigZagTestLog(xml, zz)

        assert 'FAILED' == zztl.status

    def test_status_skip(self, single_skip_xml, mocker):
        """Verify the status property when we expect a skip"""

        # Setup
        zz = mocker.MagicMock()
        junit_xml_doc = etree.parse(single_skip_xml)
        junit_xml = junit_xml_doc.getroot()
        xml = junit_xml.find('testcase')

        zztl = _ZigZagTestLog(xml, zz)

        assert 'SKIPPED' == zztl.status

    def test_status_failed(self, single_fail_xml, mocker):
        """Verify the status property when we expect a failure"""

        # Setup
        zz = mocker.MagicMock()
        junit_xml_doc = etree.parse(single_fail_xml)
        junit_xml = junit_xml_doc.getroot()
        xml = junit_xml.find('testcase')

        zztl = _ZigZagTestLog(xml, zz)

        assert 'FAILED' == zztl.status

    def test_name_property(self, single_passing_xml, mocker):
        """Verify the name property"""

        # Setup
        zz = mocker.MagicMock()
        junit_xml_doc = etree.parse(single_passing_xml)
        junit_xml = junit_xml_doc.getroot()
        xml = junit_xml.find('testcase')

        zztl = _ZigZagTestLog(xml, zz)

        assert 'test_pass' == zztl.name


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
        assert tl.stderr == 'stderr'
        assert tl.stdout == 'stdout'

        # there should be a list of two attachments: the junit xml
        # file and a text log
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 4
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'

        for test_log_attachment in tl.qtest_test_log.attachments[1:]:
            assert test_log_attachment.content_type == 'text/plain'

    def test_failed_test_case_attachments_no_sys_capture(self, single_failing_no_sys_capture_xml, mock_zigzag):
        """Test to ensure that the correct test artifacts are being attached when the JUnitXML testcase element does
        not contain 'system-err' or 'system-out' elements.
        """

        # Setup
        mock_zigzag()
        zz = ZigZag(single_failing_no_sys_capture_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class
        assert not tl.stderr
        assert not tl.stdout

        # there should be a list of two attachments: the junit xml
        # file and a text log
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 2
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'
        assert tl.qtest_test_log.attachments[1].content_type == 'text/plain'

    def test_failed_test_case_attachments_duplicate_sys_capture(self,
                                                                single_failing_duplicate_sys_capture_xml,
                                                                mock_zigzag):
        """Test to ensure that the correct test artifacts are being attached when the JUnitXML testcase element has
        duplicate 'system-err' and 'system-out' elements. Expected behavior is to select the first set of elements for
        data extraction. (See ASC-1141)
        """

        # Setup
        mock_zigzag()
        zz = ZigZag(single_failing_duplicate_sys_capture_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class
        assert tl.stderr == 'stderr'
        assert tl.stdout == 'stdout'

        # there should be a list of two attachments: the junit xml
        # file and a text log
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 4
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'

        for test_log_attachment in tl.qtest_test_log.attachments[1:]:
            assert test_log_attachment.content_type == 'text/plain'

    def test_failed_test_case_attachments_missing_sys_err(self, single_failing_missing_sys_err_xml, mock_zigzag):
        """Test to ensure that the correct test artifacts are being attached when the JUnitXML testcase element does
        not contain the 'system-err' element.
        """

        # Setup
        mock_zigzag()
        zz = ZigZag(single_failing_missing_sys_err_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class
        assert not tl.stderr
        assert tl.stdout == 'stdout'

        # there should be a list of two attachments: the junit xml
        # file and a text log
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 3
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'

        for test_log_attachment in tl.qtest_test_log.attachments[1:]:
            assert test_log_attachment.content_type == 'text/plain'

    def test_failed_test_case_attachments_missing_sys_out(self, single_failing_missing_sys_out_xml, mock_zigzag):
        """Test to ensure that the correct test artifacts are being attached when the JUnitXML testcase element does
        not contain the 'system-out' element.
        """

        # Setup
        mock_zigzag()
        zz = ZigZag(single_failing_missing_sys_out_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class
        assert tl.stderr == 'stderr'
        assert not tl.stdout

        # there should be a list of two attachments: the junit xml
        # file and a text log
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 3
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'

        for test_log_attachment in tl.qtest_test_log.attachments[1:]:
            assert test_log_attachment.content_type == 'text/plain'

    def test_failed_test_step_attachments(self, single_test_with_mixed_status_steps_xml, mock_zigzag):
        """Test to ensure that test artifacts are being correctly attached to test steps upon failure."""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_test_with_mixed_status_steps_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]
        assert tl.stderr == 'stderr'
        assert tl.stdout == 'stdout'

        # The test log should have the junit xml file, failure, stderr and stdout text logs attached.
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 4
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'

        for test_log_attachment in tl.qtest_test_log.attachments[1:]:
            assert test_log_attachment.content_type == 'text/plain'

        # The failing step should have a failure log, stderr and stdout text logs attached.
        failing_step = tl.qtest_test_log.test_step_logs[1]      # Failing step at known location.
        assert len(failing_step.attachments) == 3

        for failing_test_log_attachment in failing_step.attachments:
            assert failing_test_log_attachment.content_type == 'text/plain'

    def test_failed_test_step_attachments_no_sys_capture(self,
                                                         single_test_with_mixed_status_steps_no_sys_capture_xml,
                                                         mock_zigzag):
        """Test to ensure that test artifacts are being correctly attached to test steps upon failure."""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_test_with_mixed_status_steps_no_sys_capture_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]
        assert not tl.stderr
        assert not tl.stdout

        # The test log should have the junit xml file and failure text log attached.
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 2
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'
        assert tl.qtest_test_log.attachments[1].content_type == 'text/plain'

        # The failing step should have a failure text log attached.
        failing_step = tl.qtest_test_log.test_step_logs[1]      # Failing step at known location.
        assert len(failing_step.attachments) == 1

    def test_failed_test_step_attachments_missing_sys_err_xml(self,
                                                              single_test_with_mixed_status_steps_missing_sys_err_xml,
                                                              mock_zigzag):
        """Test to ensure that test artifacts are being correctly attached to test steps upon failure."""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_test_with_mixed_status_steps_missing_sys_err_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]
        assert not tl.stderr
        assert tl.stdout == 'stdout'

        # The test log should have the junit xml file, failure and stdout text logs attached.
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 3
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'

        for test_log_attachment in tl.qtest_test_log.attachments[1:]:
            assert test_log_attachment.content_type == 'text/plain'

        # The failing test log should have the junit xml file, failure and stdout text logs attached.
        failing_step = tl.qtest_test_log.test_step_logs[1]      # Failing step at known location.
        assert len(failing_step.attachments) == 2

        for failing_test_log_attachment in failing_step.attachments:
            assert failing_test_log_attachment.content_type == 'text/plain'

    def test_failed_test_step_attachments_missing_sys_out_xml(self,
                                                              single_test_with_mixed_status_steps_missing_sys_out_xml,
                                                              mock_zigzag):
        """Test to ensure that test artifacts are being correctly attached to test steps upon failure."""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_test_with_mixed_status_steps_missing_sys_out_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]
        assert tl.stderr == 'stderr'
        assert not tl.stdout

        # The test log should have the junit xml file, failure and stderr text logs attached.
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 3
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'

        for test_log_attachment in tl.qtest_test_log.attachments[1:]:
            assert test_log_attachment.content_type == 'text/plain'

            # The failing test log should have the junit xml file, failure and stderr text logs attached.
        failing_step = tl.qtest_test_log.test_step_logs[1]      # Failing step at known location.
        assert len(failing_step.attachments) == 2

        for failing_test_log_attachment in failing_step.attachments:
            assert failing_test_log_attachment.content_type == 'text/plain'

    def test_truncated_failure_output(self, single_fail_xml, mock_zigzag):
        """Test to ensure that log messages are truncated correctly"""

        # Setup
        mock_zigzag()
        zz = ZigZag(single_fail_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class

        assert len(tl.failure_output.split('\n')) == 4

    def test_truncated_failure_output_with_short_single_line_message(self, short_single_line_failure_message,
                                                                     mock_zigzag):
        """Verify that a failure output of only one line will NOT be truncated."""

        # Setup
        mock_zigzag()
        zz = ZigZag(short_single_line_failure_message, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class

        assert tl.failure_output == 'Short'

    def test_truncated_failure_output_with_long_single_line_message(self, long_single_line_failure_message,
                                                                    mock_zigzag):
        """Verify that a failure output of only one line will NOT be truncated."""

        # Setup
        mock_zigzag()
        zz = ZigZag(long_single_line_failure_message, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class

        assert tl.failure_output == LONG_FAILURE_MESSAGE[:120] + '...'

    def test_truncated_failure_output_with_long_multi_line_message(self, long_multi_line_failure_message, mock_zigzag):
        """Verify that a failure output of only one line will NOT be truncated."""

        # Setup
        mock_zigzag()
        zz = ZigZag(long_multi_line_failure_message, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.parse()

        # Test
        tl = ZigZagTestLogs(zz)[0]  # Create a new TestLog object through the ZigZagTestLogs public class

        assert len(tl.failure_output.split('\n')) == 4
        assert 'Log truncated' in tl._failure_output
        assert '{}{}'.format(LONG_FAILURE_MESSAGE[:100], '...') in tl._failure_output

    def test_attempt_parse_old_xml(self, test_without_test_step, mock_zigzag):
        """Verify that an error will be raised when we attempt to raise an parse xml generated by an old tool"""
        # Setup
        mock_zigzag()
        zz = ZigZag(test_without_test_step, TOKEN, PROJECT_ID, TEST_CYCLE)

        with pytest.raises(ZigZagTestLogError, message='Test found without test_step property'):
            zz.parse()


class TestZigZagTestLogsTempest(object):
    """Tests for the TestLog class"""

    def test_tempest_xml_with_none_for_execution_parameters(self, tempest_xml_with_none_for_exec_params, mocker):
        """Verify the status property when we expect a skip"""

        zz = mocker.MagicMock()
        zztlt = _ZigZagTestLogTempest(tempest_xml_with_none_for_exec_params, zz)

        assert zztlt.test_execution_parameters == []

    def test_tempest_xml_with_no_execution_parameters(self, tempest_xml_with_no_exec_params, mocker):
        """Verify the status property when we expect a skip"""

        zz = mocker.MagicMock()
        zztlt = _ZigZagTestLogTempest(tempest_xml_with_no_exec_params, zz)

        assert zztlt.test_execution_parameters == ['']

    def test_tempest_xml_with_some_none_execution_parameters(self, tempest_xml_with_some_none_exec_params, mocker):
        """Verify the status property when we expect a skip"""

        zz = mocker.MagicMock()
        zztlt = _ZigZagTestLogTempest(tempest_xml_with_some_none_exec_params, zz)

        assert zztlt.test_execution_parameters == ['foo', '', 'bar', '']

    def test_sample_tempest_xml_with_empty_execution_parameters(self, tempest_case_xml_with_empty_exec_params, mocker):
        """Verify the status property when we expect a skip"""

        zz = mocker.MagicMock()
        zztlt = _ZigZagTestLogTempest(tempest_case_xml_with_empty_exec_params, zz)

        assert zztlt.test_execution_parameters == ['', '', '', '']

    def test_sample_tempest_xml_with_execution_parameters(self, tempest_case_xml_with_execution_parameters, mocker):
        """Verify the status property when we expect a skip"""

        zz = mocker.MagicMock()
        zztlt = _ZigZagTestLogTempest(tempest_case_xml_with_execution_parameters, zz)

        assert zztlt.test_execution_parameters == ['compute',
                                                   'id-7fff3fb3-91d8-4fd0-bd7d-0204f1f180ba',
                                                   'network',
                                                   'smoke']

    def test_sample_tempest_xml(self, tempest_xml, mock_zigzag):
        """Verify that we can parse xml generated by tempest"""

        # Setup
        mock_zigzag()
        zz = ZigZag(tempest_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.test_runner = 'tempest'
        zz.parse()

        # Test
        tls = ZigZagTestLogs(zz)

        assert 8 == len(tls)  # number of tests parsed

    def test_calculate_time(self, tempest_xml, mock_zigzag):
        """Verify that we can calculate the end time based on the time attribute"""

        # Setup
        mock_zigzag()
        zz = ZigZag(tempest_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.test_runner = 'tempest'
        zz.parse()

        # Test
        for tl in ZigZagTestLogs(zz):
            start = datetime.strptime(tl.start_date, _ZigZagTestLog._date_time_format)
            end = datetime.strptime(tl.end_date, _ZigZagTestLog._date_time_format)
            assert end > start

    def test_start_date(self, tempest_case_xml_passed, mocker):
        """Verify that start_date will be now for tempest"""

        zz = mocker.MagicMock()
        zz._start_date = None  # set to none to allow lazy load
        zztlt = _ZigZagTestLogTempest(tempest_case_xml_passed, zz)

        start = datetime.strptime(zztlt.start_date, _ZigZagTestLog._date_time_format)
        now = datetime.utcnow()
        margin = timedelta(seconds=2)

        # test that the start_date is within +-2 seconds of now
        assert now - margin <= start <= now + margin

    def test_automation_content(self, tempest_xml, mock_zigzag):
        """Verify that we can get the UUID from the XML or we get none back"""

        # Setup
        mock_zigzag()
        zz = ZigZag(tempest_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.test_runner = 'tempest'
        zz.parse()

        # Test
        for tl in ZigZagTestLogs(zz):
            try:
                assert UUID(tl.automation_content)
            except ZigZagTestLogError:  # case where we do not have a UUID
                pass

    def test_name_property(self, tempest_case_xml_passed, mocker):
        """Verify that we can correctly derive the name from the xml"""

        zz = mocker.MagicMock()
        zztlt = _ZigZagTestLogTempest(tempest_case_xml_passed, zz)

        assert 'test_password_history_not_enforced_in_admin_reset' == zztlt.name

    def test_qtest_test_log_generation(self, tempest_xml, mock_zigzag):
        """Verify that we can generate qtest_test_log objects"""

        # Setup
        mock_zigzag()
        zz = ZigZag(tempest_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        zz.test_runner = 'tempest'
        zz.parse()

        # Test
        for tl in ZigZagTestLogs(zz):
            try:
                assert tl.qtest_test_log
            except ZigZagTestLogError:  # case where we do not have a UUID
                pass

    def test_status_skip(self, tempest_case_xml_skip, mocker):
        """Verify the status property when we expect a skip"""

        zz = mocker.MagicMock()
        zztlt = _ZigZagTestLogTempest(tempest_case_xml_skip, zz)

        assert 'SKIPPED' == zztlt.status

    def test_status_passed(self, tempest_case_xml_passed, mocker):
        """Verify the status property when we expect a pass"""

        zz = mocker.MagicMock()
        zztlt = _ZigZagTestLogTempest(tempest_case_xml_passed, zz)

        assert 'PASSED' == zztlt.status

    def test_status_error(self, tempest_case_xml_error, mocker):
        """Verify the status property when we expect a error"""

        zz = mocker.MagicMock()
        zztlt = _ZigZagTestLogTempest(tempest_case_xml_error, zz)

        assert 'FAILED' == zztlt.status

    def test_status_failed(self, tempest_case_xml_failed, mocker):
        """Verify the status property when we expect a error"""

        zz = mocker.MagicMock()
        zztlt = _ZigZagTestLogTempest(tempest_case_xml_failed, zz)

        assert 'FAILED' == zztlt.status
