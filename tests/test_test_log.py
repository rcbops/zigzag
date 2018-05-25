#!/usr/bin/env pytho
# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import swagger_client
from zigzag.test_log import TestLog
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
class TestTestLog(object):
    """Tests for the TestLog class"""

    def test_lookup_ids(self, single_test_with_jira_tickets_xml, mocker):
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
        junit_xml_doc = etree.parse(single_test_with_jira_tickets_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = TestLog(test_case_xml, zz)

        assert tl.qtest_testcase_id == qtest_id

    def test_lookup_ids_not_found(self, single_test_with_jira_tickets_xml, mocker):
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
        junit_xml_doc = etree.parse(single_test_with_jira_tickets_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = TestLog(test_case_xml, zz)

        assert tl.qtest_testcase_id is None

    def test_lookup_requirements_not_found(self, single_test_with_jira_tickets_xml, mocker):
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
        junit_xml_doc = etree.parse(single_test_with_jira_tickets_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = TestLog(test_case_xml, zz)

        assert isinstance(tl.qtest_requirements, list)
        assert not len(tl.qtest_requirements)

    def test_lookup_requirements(self, single_test_with_jira_tickets_xml, mocker):
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
        junit_xml_doc = etree.parse(single_test_with_jira_tickets_xml)
        test_case_xml = junit_xml_doc.find('testcase')
        tl = TestLog(test_case_xml, zz)

        assert isinstance(tl.qtest_requirements, list)
        # there should be two requirements since xml has two jira marks
        assert tl.qtest_requirements == [qtest_id, qtest_id]
