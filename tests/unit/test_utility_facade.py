# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import swagger_client
from zigzag.zigzag import ZigZag
from zigzag.utility_facade import UtilityFacade
import requests
import json

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
class TestFindCustomFieldByLabel(object):
    """Test cases for find_custom_field_by_label()"""

    def test_happy_path(self, single_fail_xml, mocker):
        """The happy path"""
        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)

        # Setup
        zz = ZigZag(single_fail_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        uf = UtilityFacade(zz)

        result = uf.find_custom_field_id_by_label('Failure Output', 'test-runs')
        assert result == 12345

    def test_label_not_found(self, single_fail_xml, mocker):
        """Search for a label that does not exist"""
        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'foo'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)

        # Setup
        zz = ZigZag(single_fail_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        uf = UtilityFacade(zz)

        result = uf.find_custom_field_id_by_label('Failure Output', 'test-runs')
        assert result is None
