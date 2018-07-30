# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import swagger_client
from zigzag.zigzag_test_log import ZigZagTestLog
import requests
import json
from lxml import etree


# ======================================================================================================================
# Globals
# ======================================================================================================================

# Shared variables
TOKEN = 'VALID_TOKEN'
PROJECT_ID = 12345
TEST_CYCLE = 'CL-1'


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
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

    def test_log_truncation(self, single_fail_xml, mocker):
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

        assert len(tl._failure_output) == \
            len(tl._max_log_message_length_notification) + tl._max_log_message_length
