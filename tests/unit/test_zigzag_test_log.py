# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import json
import pytest
import requests
import swagger_client
from lxml import etree
from zigzag.zigzag_test_log import ZigZagTestLog
from .conftest import DEFAULT_GLOBAL_PROPERTIES, DEFAULT_TESTCASE_PROPERTIES


# ======================================================================================================================
# Globals
# ======================================================================================================================
TOKEN = 'VALID_TOKEN'
PROJECT_ID = 12345
TEST_CYCLE = 'CL-1'
LONG_FAILURE_MESSAGE = ('This is a very long failure message produced by a test fixture in order to validate that the '
                        'failure output truncation works as intended because clowns!')


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
@pytest.fixture
def short_single_line_failure_message(tmpdir_factory):
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
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture
def long_single_line_failure_message(tmpdir_factory):
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
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES,
                   testcase_properties=DEFAULT_TESTCASE_PROPERTIES,
                   failure_message=LONG_FAILURE_MESSAGE)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture
def long_multi_line_failure_message(tmpdir_factory):
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
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES,
                   testcase_properties=DEFAULT_TESTCASE_PROPERTIES,
                   failure_message=LONG_FAILURE_MESSAGE)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
# noinspection PyProtectedMember
class TestZigZagTestLog(object):
    """Tests for the TestLog class"""

    def test_lookup_ids(self, single_passing_xml, mocker):
        """Test for _lookup_ids happy path"""
        qtest_id = 123456789
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 1,
            "items": [
                {
                    "id": qtest_id,
                    "name": "PRO-18405 Fake!"
                }
            ]
        }

        # a mock for a ZigZag object
        zz = mocker.MagicMock()
        zz._qtest_api_token = 'totally real'
        zz._qtest_project_id = '54321'

        # patch the API calls
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # create a new TestLog object with fixture xml and the zz object
        junit_xml_doc = etree.parse(single_passing_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = ZigZagTestLog(test_case_xml, zz)

        assert tl.qtest_testcase_id == qtest_id

    def test_lookup_ids_not_found(self, single_passing_xml, mocker):
        """Test for _lookup_ids
        Ask for a test ID that does not exist yet
        """
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 0,
            "items": []
        }

        # a mock for a ZigZag object
        zz = mocker.MagicMock()
        zz._qtest_api_token = 'totally real'
        zz._qtest_project_id = '54321'

        # patch the API calls
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # create a new TestLog object with fixture xml and the zz object
        junit_xml_doc = etree.parse(single_passing_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = ZigZagTestLog(test_case_xml, zz)

        assert tl.qtest_testcase_id is None

    def test_lookup_requirements_not_found(self, single_passing_xml, mocker):
        """Test for _lookup_requirements
        Ask for a requirements that have not been imported from jira yet
        """
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 0,
            "items": []
        }

        # a mock for a ZigZag object
        zz = mocker.MagicMock()
        zz._qtest_api_token = 'totally real'
        zz._qtest_project_id = '54321'

        # patch the API calls
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # create a new TestLog object with fixture xml and the zz object
        junit_xml_doc = etree.parse(single_passing_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = ZigZagTestLog(test_case_xml, zz)

        assert isinstance(tl.qtest_requirements, list)
        assert not len(tl.qtest_requirements)

    def test_lookup_requirements(self, single_passing_xml, mocker):
        """Test for _lookup_requirements
        Ask for two requirements that correspond to jira ids
        """
        qtest_id = 123456789
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 1,
            "items": [
                {
                    "id": qtest_id,
                    "name": "PRO-18405 Fake!"
                }
            ]
        }

        # a mock for a ZigZag object
        zz = mocker.MagicMock()
        zz._qtest_api_token = 'totally real'
        zz._qtest_project_id = '54321'

        # patch the API calls
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # create a new TestLog object with fixture xml and the zz object
        junit_xml_doc = etree.parse(single_passing_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = ZigZagTestLog(test_case_xml, zz)

        assert isinstance(tl.qtest_requirements, list)
        # there should be two requirements since xml has two jira marks
        assert tl.qtest_requirements == [qtest_id, qtest_id]

    def test_successful_test_case_attachments(self, single_passing_xml, mocker):
        """Test to ensure that test artifacts are being correctly attached
        Ensure that there is only one attachment (junit.xml) in the passing case.
        """
        qtest_id = 123456789
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 1,
            "items": [
                {
                    "id": qtest_id,
                    "name": "PRO-18405 Fake!"
                }
            ]
        }

        # a mock for a ZigZag object
        zz = mocker.MagicMock()
        zz._qtest_api_token = 'totally real'
        zz._qtest_project_id = '54321'

        # patch the API calls
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # create a new TestLog object with fixture xml and the zz object
        junit_xml_doc = etree.parse(single_passing_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = ZigZagTestLog(test_case_xml, zz)
        tl._mediator.serialized_junit_xml = etree.tostring(junit_xml_doc)

        # there should be a list of two attachments: the junit xml
        # file and a text log
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 1
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'


# noinspection PyProtectedMember
class TestFailedTestCases(object):
    """Tests for failure output messagage and failure log attachment."""

    def test_failed_test_case_attachments(self, single_fail_xml, mocker):
        """Test to ensure that test artifacts are being correctly attached
        Ensure that there are two attachments, one of type xml and one of type
        text.
        """

        qtest_id = 123456789
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 1,
            "items": [
                {
                    "id": qtest_id,
                    "name": "PRO-18405 Fake!"
                }
            ]
        }

        # a mock for a ZigZag object
        zz = mocker.MagicMock()
        zz._qtest_api_token = 'totally real'
        zz._qtest_project_id = '54321'

        # patch the API calls
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # create a new TestLog object with fixture xml and the zz object
        junit_xml_doc = etree.parse(single_fail_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = ZigZagTestLog(test_case_xml, zz)
        tl._mediator.serialized_junit_xml = etree.tostring(junit_xml_doc)

        # there should be a list of two attachments: the junit xml
        # file and a text log
        assert isinstance(tl.qtest_test_log.attachments, list)
        assert len(tl.qtest_test_log.attachments) == 2
        assert tl.qtest_test_log.attachments[0].content_type == 'application/xml'
        assert tl.qtest_test_log.attachments[1].content_type == 'text/plain'

    def test_truncated_failure_output(self, single_fail_xml, mocker):
        """Test to ensure that log messages are truncated correctly"""

        qtest_id = 123456789
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 1,
            "items": [
                {
                    "id": qtest_id,
                    "name": "PRO-18405 Fake!"
                }
            ]
        }

        # a mock for a ZigZag object
        zz = mocker.MagicMock()
        zz._qtest_api_token = 'totally real'
        zz._qtest_project_id = '54321'

        # patch the API calls
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # create a new TestLog object with fixture xml and the zz object
        junit_xml_doc = etree.parse(single_fail_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = ZigZagTestLog(test_case_xml, zz)
        tl._mediator.serialized_junit_xml = etree.tostring(junit_xml_doc)

        assert len(tl._failure_output.split('\n')) == 4

    def test_truncated_failure_output_with_short_single_line_message(self, short_single_line_failure_message, mocker):
        """Verify that a failure output of only one line will NOT be truncated."""

        qtest_id = 123456789
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 1,
            "items": [
                {
                    "id": qtest_id,
                    "name": "PRO-18405 Fake!"
                }
            ]
        }

        # a mock for a ZigZag object
        zz = mocker.MagicMock()
        zz._qtest_api_token = 'totally real'
        zz._qtest_project_id = '54321'

        # patch the API calls
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # create a new TestLog object with fixture xml and the zz object
        junit_xml_doc = etree.parse(short_single_line_failure_message)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = ZigZagTestLog(test_case_xml, zz)
        tl._mediator.serialized_junit_xml = etree.tostring(junit_xml_doc)

        assert tl._failure_output == 'Short'

    def test_truncated_failure_output_with_long_single_line_message(self, long_single_line_failure_message, mocker):
        """Verify that a failure output of only one line will NOT be truncated."""

        qtest_id = 123456789
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 1,
            "items": [
                {
                    "id": qtest_id,
                    "name": "PRO-18405 Fake!"
                }
            ]
        }

        # a mock for a ZigZag object
        zz = mocker.MagicMock()
        zz._qtest_api_token = 'totally real'
        zz._qtest_project_id = '54321'

        # patch the API calls
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # create a new TestLog object with fixture xml and the zz object
        junit_xml_doc = etree.parse(long_single_line_failure_message)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = ZigZagTestLog(test_case_xml, zz)
        tl._mediator.serialized_junit_xml = etree.tostring(junit_xml_doc)

        assert tl._failure_output == LONG_FAILURE_MESSAGE[:120] + '...'

    def test_truncated_failure_output_with_long_multi_line_message(self, long_multi_line_failure_message, mocker):
        """Verify that a failure output of only one line will NOT be truncated."""

        qtest_id = 123456789
        search_response = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 1,
            "items": [
                {
                    "id": qtest_id,
                    "name": "PRO-18405 Fake!"
                }
            ]
        }

        # a mock for a ZigZag object
        zz = mocker.MagicMock()
        zz._qtest_api_token = 'totally real'
        zz._qtest_project_id = '54321'

        # patch the API calls
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(search_response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # create a new TestLog object with fixture xml and the zz object
        junit_xml_doc = etree.parse(long_multi_line_failure_message)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = ZigZagTestLog(test_case_xml, zz)
        tl._mediator.serialized_junit_xml = etree.tostring(junit_xml_doc)

        assert len(tl._failure_output.split('\n')) == 4
        assert 'Log truncated' in tl._failure_output
        assert '{}{}'.format(LONG_FAILURE_MESSAGE[:100], '...') in tl._failure_output
