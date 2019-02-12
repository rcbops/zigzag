# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import swagger_client
from zigzag.zigzag import ZigZag
from zigzag.requirements_link_facade import RequirementsLinkFacade
import requests
import json

# ======================================================================================================================
# Globals
# ======================================================================================================================

# Shared variables
TOKEN = 'VALID_TOKEN'
PROJECT_ID = 12345
TEST_CYCLE = 'CL-1'

SEARCH_REQUIRMENT_RESPONSE = {
    "links": [],
    "page": 1,
    "page_size": 100,
    "total": 8,
    "items": [
        {
            "id": 9334830,
            "name": "PRO-18405 Fake!"
        },
        {
            "id": 9325865,
            "name": "PRO-18404 Zach's requirement"
        },
        {
            "id": 9252653,
            "name": "PRO-18398 Ryan - Requirement #1"
        },
        {
            "id": 9252764,
            "name": "PRO-18403 Ryan - Sub-requirement #2"
        },
        {
            "id": 9252762,
            "name": "PRO-18402 Ryan - Sub-requirement #1"
        },
        {
            "id": 9252759,
            "name": "PRO-18401 Ryan - Requirement #4"
        },
        {
            "id": 9252758,
            "name": "PRO-18400 Ryan - Requirement #3"
        },
        {
            "id": 9252652,
            "name": "PRO-18399 Ryan - Requirement #2"
        }
    ]
}


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestRequirementsLinkFacade(object):
    """Tests for the link() function"""

    def test_link(self, single_passing_xml, asc_zigzag_config_file, mocker):
        """The happy path"""

        id = 8675309
        response_body = {
            "links": [],
            "page": 1,
            "page_size": 100,
            "total": 1,
            "items": [
                {
                    "id": id,
                    "name": 'This is the name'
                }
            ]
        }
        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.SearchApi.search', return_value=response_body)
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts')
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response_body)
        mocker.patch('requests.post', return_value=mock_post_response)

        # Setup
        zz = ZigZag(single_passing_xml, asc_zigzag_config_file, TOKEN)
        zz.parse()
        rlf = RequirementsLinkFacade(zz)
        log = zz.test_logs[0]

        # Test
        rlf.link()

        # After think link we should have much more information about linked resource
        assert ['ASC-123', 'ASC-456'] == log.jira_issues
        assert [id, id] == log.qtest_requirements
        assert id == log.qtest_testcase_id

    def test_link_test_case_not_created_yet(self, single_passing_xml, asc_zigzag_config_file, mocker):
        """The happy path"""

        response_body = {
            "links": [],
            "page": 1,
            "page_size": 1,
            "total": 0,
            "items": []
        }
        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.SearchApi.search', return_value=response_body)
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts')
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response_body)
        mocker.patch('requests.post', return_value=mock_post_response)

        # Setup
        zz = ZigZag(single_passing_xml, asc_zigzag_config_file, TOKEN)
        zz.parse()
        rlf = RequirementsLinkFacade(zz)
        log = zz.test_logs[0]

        # Test
        rlf.link()

        # After think link we should have much more information about linked resource
        assert ['ASC-123', 'ASC-456'] == log.jira_issues
        assert [] == log.qtest_requirements
        assert log.qtest_testcase_id is None
