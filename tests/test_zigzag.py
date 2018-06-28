#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import re
import pytest
import swagger_client
from hashlib import md5
from zigzag.zigzag import ZigZag
from swagger_client.rest import ApiException
import requests
import json

# ======================================================================================================================
# Globals
# ======================================================================================================================
# Shared expectations
SHARED_TEST_LOG_EXP = {'build_url': 'BUILD_URL',
                       'build_number': 'BUILD_NUMBER',
                       'module_names': ['RPC_RELEASE',
                                        'JOB_NAME',
                                        'MOLECULE_TEST_REPO',
                                        'MOLECULE_SCENARIO_NAME',
                                        'test_default'],
                       'automation_content': '1',
                       'exe_start_date': '2018-04-10T21:38:18Z',
                       'exe_end_date': '2018-04-10T21:38:19Z'}
# Shared variables
TOKEN = 'VALID_TOKEN'
PROJECT_ID = 12345
TEST_CYCLE = 'CL-1'


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestZigZag(object):
    """Test cases for ZigZag as a moderator object"""

    def test_data_stored_on_mediator(self, flat_all_passing_xml, mocker):
        """verify that the ZigZag object stores properties after initialization"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 2983472
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(flat_all_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        assert zz.qtest_project_id == 12345
        assert len(zz.test_logs)
        assert zz.build_url == 'BUILD_URL'
        assert zz.junit_xml is not None
        assert zz.build_number == 'BUILD_NUMBER'
        assert zz.pprint_on_fail is False
        assert zz.testsuite_props


class TestLoadingInputJunitXMLFile(object):
    """Test cases for the loading of a JUnitXML file"""

    def test_load_file_happy_path(self, flat_all_passing_xml, mocker):
        """Verify that a valid JUnitXML file can be loaded"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(flat_all_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Expectations
        root_tag_atribute_exp = {'errors': '0',
                                 'failures': '0',
                                 'name': 'pytest',
                                 'skips': '0',
                                 'tests': '5',
                                 'time': '1.664'}

        # Test
        assert root_tag_atribute_exp == zz._junit_xml.attrib

    def test_invalid_file_path(self, mocker):
        """Verify that an invalid file path raises an exception"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            ZigZag('/path/does/not/exist', TOKEN, PROJECT_ID, TEST_CYCLE)

    def test_invalid_xml_content(self, bad_xml, mocker):
        """Verify that invalid XML file content raises an exception"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            ZigZag(bad_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

    def test_missing_junit_xml_root(self, bad_junit_root, mocker):
        """Verify that XML files missing the expected JUnitXML root element raises an exception"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            ZigZag(bad_junit_root, TOKEN, PROJECT_ID, TEST_CYCLE)

    def test_missing_build_url_xml(self, missing_build_url_xml, mocker):
        """Verify that JUnitXML that is missing the test suite 'BUILD_URL' property element causes a RuntimeError."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            ZigZag(missing_build_url_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

    def test_missing_testcase_properties_xml(self, missing_testcase_properties_xml, mocker):
        """Verify that JUnitXML that is missing the test case 'properties' element causes a RuntimeError."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            ZigZag(missing_testcase_properties_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

    def test_missing_test_id_xml(self, missing_test_id_xml, mocker):
        """Verify that JUnitXML that is missing the 'test_id' test case property causes a RuntimeError."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            ZigZag(missing_test_id_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

    def test_exceeds_max_file_size(self, flat_all_passing_xml, mocker):
        """Verify that XML files that exceed the max file size are rejected"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        file_size = 52428801

        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('os.path.getsize', return_value=file_size)

        # Test
        with pytest.raises(RuntimeError):
            ZigZag(flat_all_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

    def test_schema_violation_with_pprint_on_fail(self, missing_test_id_xml, mocker):
        """Verify that JUnitXML that violates the schema with 'pprint_on_fail' enabled with emit an error message with
        the XML pretty printed in the error message."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Expectations
        error_msg_exp = '---DEBUG XML PRETTY PRINT---'

        # Test
        try:
            ZigZag(missing_test_id_xml, TOKEN, PROJECT_ID, TEST_CYCLE, pprint_on_fail=True)
        except RuntimeError as e:
            assert error_msg_exp in str(e)


# noinspection PyUnresolvedReferences
class TestParseXMLtoTestLogs(object):
    """Test cases for zigzags parsing of raw junit.xml into TestLog objects
    This tests the parsing logic inside of the parsing facade
    """

    def test_pass(self, single_passing_xml, mocker):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a single passing test.
        """
        object_id = 12345

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = object_id
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': object_id}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log = zz.test_logs[0]

        assert test_log.name == 'test_pass'
        assert test_log.status == 'PASSED'
        assert test_log.failure_output == ''
        assert test_log.start_date == '2018-04-10T21:38:18Z'
        assert test_log.end_date == '2018-04-10T21:38:19Z'
        assert test_log.jira_issues == ['ASC-123', 'ASC-456']
        assert test_log.automation_content == '1'
        assert test_log.qtest_requirements == [object_id, object_id]
        assert test_log.qtest_testcase_id == object_id  # We look this up on instantiation of a TestLog

    def test_fail(self, single_fail_xml, mocker):
        """Verify that a JUnitXML failing test will parse into a TestLog.
        """

        object_id = 12345

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = object_id
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': object_id}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(single_fail_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log = zz.test_logs[0]

        assert test_log.name == 'test_fail'
        assert test_log.status == 'FAILED'
        assert 'def test_fail(host):' in test_log.failure_output
        assert test_log.start_date == '2018-04-10T21:38:18Z'
        assert test_log.end_date == '2018-04-10T21:38:19Z'
        assert test_log.jira_issues == ['ASC-123', 'ASC-456']
        assert test_log.automation_content == '1'
        assert test_log.qtest_requirements == [object_id, object_id]
        assert test_log.qtest_testcase_id == object_id

    def test_error(self, single_error_xml, mocker):
        """Verify that a JUnitXML error test will parse into a single TestLog.
        """

        object_id = 12345

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = object_id
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': object_id}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(single_error_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log = zz.test_logs[0]

        assert test_log.name == 'test_error'
        assert test_log.status == 'FAILED'
        assert 'def error_fixture(host):' in test_log.failure_output
        assert test_log.start_date == '2018-04-10T21:38:18Z'
        assert test_log.end_date == '2018-04-10T21:38:19Z'
        assert test_log.jira_issues == ['ASC-123', 'ASC-456']
        assert test_log.automation_content == '1'
        assert test_log.qtest_requirements == [object_id, object_id]
        assert test_log.qtest_testcase_id == object_id

    def test_skip(self, single_skip_xml, mocker):
        """Verify that a JUnitXML skipped test will parse into a single TestLog.
        """

        object_id = 12345

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = object_id
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': object_id}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(single_skip_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log = zz.test_logs[0]

        assert test_log.name == 'test_skip'
        assert test_log.status == 'SKIPPED'
        assert test_log.failure_output == ''
        assert test_log.start_date == '2018-04-10T21:38:18Z'
        assert test_log.end_date == '2018-04-10T21:38:19Z'
        assert test_log.jira_issues == ['ASC-123', 'ASC-456']
        assert test_log.automation_content == '1'
        assert test_log.qtest_requirements == [object_id, object_id]
        assert test_log.qtest_testcase_id == object_id

    def test_suite_with_tests(self, suite_all_passing_xml, mocker):
        """Verify that a JUnitXML test suite will parse into multiple TestLogs.
        """

        object_id = 12345

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = object_id
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': object_id}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(suite_all_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_logs = zz.test_logs

        # Test
        for log in test_logs:
            assert 'PASSED' == log.status
            assert re.match("test_pass\d", log.name)

    def test_junit_xml_attachment(self, single_passing_xml, mocker):
        """Verify that an xml file is attached to the qTest testlog
        """

        object_id = 12345

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = object_id
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': object_id}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log_dict = zz.test_logs[0].qtest_test_log.to_dict()

        # Expectation
        attachment_exp_name_regex = re.compile(r'^junit_.+\.xml$')
        attachment_exp_content_type = 'application/xml'
        attachment_exp_data_md5 = '0551d174d82fd095c518f6230ec99c8e'

        # Test
        assert attachment_exp_name_regex.match(test_log_dict['attachments'][0]['name']) is not None
        assert attachment_exp_content_type == test_log_dict['attachments'][0]['content_type']
        assert attachment_exp_data_md5 == md5(test_log_dict['attachments'][0]['data'].encode('UTF-8')).hexdigest()

    def test_classname_containing_dashes(self, classname_with_dashes_xml, mocker):
        """Verify that JUnitXML that has a 'classname' containing dashes (captured from the py.test filename) is
        validated correctly.
        """

        object_id = 12345

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = object_id
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': object_id}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(classname_with_dashes_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log_dict = zz.test_logs[0].qtest_test_log.to_dict()

        # Expectation
        test_name = 'test_verify_kibana_horizon_access_with_no_ssh'
        module_names = ['RPC_RELEASE',
                        'JOB_NAME',
                        'MOLECULE_TEST_REPO',
                        'MOLECULE_SCENARIO_NAME',
                        'test_for_acs-150',
                        'TestForRPC10PlusPostDeploymentQCProcess']
        test_log_exp = pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': test_name,
                                                                        'status': 'PASSED',
                                                                        'module_names': module_names})

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_invalid_classname(self, invalid_classname_xml, mocker):
        """Verify that JUnitXML that has an invalid 'classname' attribute for a testcase raises a RuntimeError."""

        object_id = 12345

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = object_id
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': object_id}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])
        # Setup
        zz = ZigZag(invalid_classname_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        with pytest.raises(RuntimeError):
            zz.test_logs[0].qtest_test_log


# noinspection PyUnresolvedReferences
class TestGenerateAutoRequest(object):
    """Test cases for the '_generate_auto_request' function"""

    def test_mix_status(self, flat_mix_status_xml, mocker):
        """Verify that a valid qTest 'AutomationRequest' swagger model is generated from a JUnitXML file
        that contains multiple tests with different status results
        """

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(flat_mix_status_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        auto_req_dict = zz._generate_auto_request().to_dict()

        # Expectation
        test_logs_exp = [pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': 'test_pass', 'status': 'PASSED'}),
                         pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': 'test_fail', 'status': 'FAILED'}),
                         pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': 'test_error', 'status': 'FAILED'}),
                         pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': 'test_skip', 'status': 'SKIPPED'})]

        # Test
        for x in range(len(auto_req_dict['test_logs'])):
            for key in test_logs_exp[x]:
                expected = test_logs_exp[x][key]
                observed = auto_req_dict['test_logs'][x][key]
                assert expected == observed


class TestUploadTestResults(object):
    """Test cases for the 'upload_test_results' function"""

    def test_happy_path(self, single_passing_xml, mocker):
        """Verify that the function can upload results from a JUnitXML file that contains a single passing test"""

        # Expectation
        job_id = '54321'

        # Mock
        mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        response = zz.upload_test_results()
        assert int(job_id) == response

    def test_api_exception(self, single_passing_xml, mocker):
        """Verify that the function fails gracefully if the API endpoint reports an API exception"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0',
                     side_effect=ApiException('Super duper failure!'))
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        with pytest.raises(RuntimeError):
            zz.upload_test_results()

    def test_job_queue_failure(self, single_passing_xml, mocker):
        """Verify that the function fails gracefully if the job queue reports a failure"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        with pytest.raises(RuntimeError):
            zz.upload_test_results()
