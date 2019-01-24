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
SHARED_TEST_LOG_EXP = {'build_url': 'https://rpc.jenkins.cit.rackspace.net/job/PM_rpc-openstack-pike-rc-xenial_mnaio_no_artifacts-swift-system/78/',  # noqa
                       'build_number': '78',
                       'module_names': ['one',
                                        'two',
                                        'three',
                                        'test_default'],
                       'automation_content': '1',
                       'exe_start_date': '2018-04-10T21:38:18Z',
                       'exe_end_date': '2018-04-10T21:38:19Z'}
# Shared variables
TOKEN = 'VALID_TOKEN'


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestZigZag(object):
    """Test cases for ZigZag as a moderator object"""

    def test_data_stored_on_mediator(self, simple_json_config, flat_all_passing_xml, mocker):
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
        zz = ZigZag(flat_all_passing_xml, simple_json_config, TOKEN)
        zz.parse()
        zz.load_config()

        # Test
        assert 12345 == zz._config_dict['project_id']
        assert len(zz.test_logs)
        assert 'https://rpc.jenkins.cit.rackspace.net/job/PM_rpc-openstack-pike-rc-xenial_mnaio_no_artifacts-swift-system/78/' == zz.build_url  # noqa
        assert zz.junit_xml is not None
        assert '78' == zz.build_number
        assert False is zz.pprint_on_fail
        assert zz.testsuite_props


class TestLoadingInputJunitXMLFile(object):
    """Test cases for the loading of a JUnitXML file"""

    def test_load_file_happy_path(self, flat_all_passing_xml, simple_json_config, mocker):
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
        zz = ZigZag(flat_all_passing_xml, simple_json_config, TOKEN)
        zz.parse()

        # Expectations
        root_tag_atribute_exp = {'errors': '0',
                                 'failures': '0',
                                 'name': 'pytest',
                                 'skips': '0',
                                 'tests': '5',
                                 'time': '1.664'}

        # Test
        # noinspection PyProtectedMember
        assert root_tag_atribute_exp == zz._junit_xml.attrib

    def test_invalid_file_path(self, simple_json_config, mocker):
        """Verify that an invalid file path raises an exception"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            zz = ZigZag('/path/does/not/exist', simple_json_config, TOKEN)
            zz.parse()

    def test_invalid_xml_content(self, bad_xml, simple_json_config, mocker):
        """Verify that invalid XML file content raises an exception"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            zz = ZigZag(bad_xml, simple_json_config, TOKEN)
            zz.parse()

    def test_missing_junit_xml_root(self, bad_junit_root, simple_json_config, mocker):
        """Verify that XML files missing the expected JUnitXML root element raises an exception"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            zz = ZigZag(bad_junit_root, simple_json_config, TOKEN)
            zz.parse()

    def test_missing_build_url_xml(self, missing_build_url_xml, simple_json_config, mocker):
        """Verify that JUnitXML that is missing the test suite 'BUILD_URL' property element causes a RuntimeError."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            zz = ZigZag(missing_build_url_xml, simple_json_config, TOKEN)
            zz.parse()

    def test_missing_testcase_properties_xml(self, missing_testcase_properties_xml, simple_json_config, mocker):
        """Verify that JUnitXML that is missing the test case 'properties' element causes a RuntimeError."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            zz = ZigZag(missing_testcase_properties_xml, simple_json_config, TOKEN)
            zz.parse()

    def test_missing_test_id_xml(self, missing_test_id_xml, simple_json_config, mocker):
        """Verify that JUnitXML that is missing the 'test_id' test case property causes a RuntimeError."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Test
        with pytest.raises(RuntimeError):
            zz = ZigZag(missing_test_id_xml, simple_json_config, TOKEN)
            zz.parse()

    def test_exceeds_max_file_size(self, flat_all_passing_xml, simple_json_config, mocker):
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
            zz = ZigZag(flat_all_passing_xml, simple_json_config, TOKEN)
            zz.parse()

    def test_schema_violation_with_pprint_on_fail(self, missing_test_id_xml, simple_json_config, mocker):
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
            zz = ZigZag(missing_test_id_xml, simple_json_config, TOKEN, pprint_on_fail=True)
            zz.parse()
        except RuntimeError as e:
            assert error_msg_exp in str(e)


# noinspection PyUnresolvedReferences
class TestParseXMLtoTestLogs(object):
    """Test cases for zigzags parsing of raw junit.xml into TestLog objects
    This tests the parsing logic inside of the parsing facade
    """

    def test_pass(self, single_passing_xml, simple_json_config, mocker):
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
        zz = ZigZag(single_passing_xml, simple_json_config, TOKEN)
        zz.parse()
        # noinspection PyUnresolvedReferences
        test_log = zz.test_logs[0]

        assert 'test_pass' == test_log.name
        assert 'PASSED' == test_log.status
        assert '' == test_log.failure_output
        assert '2018-04-10T21:38:18Z' == test_log.start_date
        assert '2018-04-10T21:38:19Z' == test_log.end_date
        assert ['ASC-123', 'ASC-456'] == test_log.jira_issues
        assert '1' == test_log.automation_content
        assert [object_id, object_id] == test_log.qtest_requirements
        assert object_id == test_log.qtest_testcase_id  # We look this up on instantiation of a TestLog

    def test_fail(self, single_fail_xml, simple_json_config, mocker):
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
        zz = ZigZag(single_fail_xml, simple_json_config, TOKEN)
        zz.parse()
        # noinspection PyUnresolvedReferences
        test_log = zz.test_logs[0]

        assert 'test_fail' == test_log.name
        assert 'FAILED' == test_log.status
        assert 'def test_fail(host):' in test_log.failure_output
        assert '2018-04-10T21:38:18Z' == test_log.start_date
        assert '2018-04-10T21:38:19Z' == test_log.end_date
        assert ['ASC-123', 'ASC-456'] == test_log.jira_issues
        assert '1' == test_log.automation_content
        assert [object_id, object_id] == test_log.qtest_requirements
        assert object_id == test_log.qtest_testcase_id

    def test_error(self, single_error_xml, simple_json_config, mocker):
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
        zz = ZigZag(single_error_xml, simple_json_config, TOKEN)
        zz.parse()
        # noinspection PyUnresolvedReferences
        test_log = zz.test_logs[0]

        assert 'test_error' == test_log.name
        assert 'FAILED' == test_log.status
        assert 'def error_fixture(host):' in test_log.failure_output \
            or 'log truncated. Please see attached log file.' in test_log.failure_output
        assert '2018-04-10T21:38:18Z' == test_log.start_date
        assert '2018-04-10T21:38:19Z' == test_log.end_date
        assert ['ASC-123', 'ASC-456'] == test_log.jira_issues
        assert '1' == test_log.automation_content
        assert [object_id, object_id] == test_log.qtest_requirements
        assert object_id == test_log.qtest_testcase_id

    def test_skip(self, single_skip_xml, simple_json_config, mocker):
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
        zz = ZigZag(single_skip_xml, simple_json_config, TOKEN)
        zz.parse()
        # noinspection PyUnresolvedReferences
        test_log = zz.test_logs[0]

        assert 'test_skip' == test_log.name
        assert 'SKIPPED' == test_log.status
        assert '' == test_log.failure_output
        assert '2018-04-10T21:38:18Z' == test_log.start_date
        assert '2018-04-10T21:38:19Z' == test_log.end_date
        assert ['ASC-123', 'ASC-456'] == test_log.jira_issues
        assert '1' == test_log.automation_content
        assert [object_id, object_id] == test_log.qtest_requirements
        assert object_id == test_log.qtest_testcase_id

    def test_suite_with_tests(self, suite_all_passing_xml, simple_json_config, mocker):
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
        zz = ZigZag(suite_all_passing_xml, simple_json_config, TOKEN)
        zz.parse()
        # noinspection PyUnresolvedReferences
        test_logs = zz.test_logs

        # Test
        for log in test_logs:
            assert 'PASSED' == log.status
            assert re.match(r'test_pass\d', log.name)

    def test_junit_xml_attachment(self, single_passing_xml, simple_json_config, mocker):
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
        zz = ZigZag(single_passing_xml, simple_json_config, TOKEN)
        zz.parse()
        zz.load_config()
        # noinspection PyUnresolvedReferences
        test_log_dict = zz.test_logs[0].qtest_test_log.to_dict()

        # Expectation
        attachment_exp_name_regex = re.compile(r'^junit_.+\.xml$')
        attachment_exp_content_type = 'application/xml'
        attachment_exp_data_md5 = 'f3b2303ccf8a76a9e20d2099e9b2f29c'

        # Test
        assert attachment_exp_name_regex.match(test_log_dict['attachments'][0]['name']) is not None
        assert attachment_exp_content_type == test_log_dict['attachments'][0]['content_type']
        assert attachment_exp_data_md5 == md5(test_log_dict['attachments'][0]['data'].encode('UTF-8')).hexdigest()

    def test_classname_containing_dashes(self, classname_with_dashes_xml, simple_json_config, mocker):
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
        zz = ZigZag(classname_with_dashes_xml, simple_json_config, TOKEN)
        zz.parse()
        zz.load_config()
        # noinspection PyUnresolvedReferences
        test_log_dict = zz.test_logs[0].qtest_test_log.to_dict()

        # Expectation
        test_name = 'test_verify_kibana_horizon_access_with_no_ssh'
        module_names = ['one',
                        'two',
                        'three',
                        'TestForRPC10PlusPostDeploymentQCProcess']
        test_log_exp = pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': test_name,
                                                                        'status': 'PASSED',
                                                                        'module_names': module_names})

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_invalid_classname(self, invalid_classname_xml, simple_json_config, mocker):
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
        zz = ZigZag(invalid_classname_xml, simple_json_config, TOKEN)
        zz.parse()
        zz.load_config()

        # Test
        with pytest.raises(RuntimeError):
            # noinspection PyStatementEffect
            zz.test_logs[0].qtest_test_log


# noinspection PyUnresolvedReferences
class TestGenerateAutoRequest(object):
    """Test cases for the '_generate_auto_request' function"""

    # noinspection PyProtectedMember
    def test_mix_status(self, flat_mix_status_xml, simple_json_config, mocker):
        """Verify that a valid qTest 'AutomationRequest' swagger model is generated from a JUnitXML file
        that contains multiple tests with different status results
        """

        # Mock
        test_cycle_name = 'queens'
        test_cycle_pid = 'CL-1'
        mock_get_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_create_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_get_tc_resp.to_dict.return_value = {'name': 'queens', 'pid': 'CL-2'}
        mock_create_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid}
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
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_get_tc_resp])
        mocker.patch('swagger_client.TestcycleApi.create_cycle', return_value=mock_create_tc_resp)

        # Setup
        zz = ZigZag(flat_mix_status_xml, simple_json_config, TOKEN)
        zz.parse()
        zz.load_config()
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

    def test_happy_path(self, single_passing_xml, simple_json_config, mocker):
        """Verify that the function can upload results from a JUnitXML file that contains a single passing test"""

        # Expectation
        job_id = '54321'

        # Mock
        test_cycle_name = 'queens'
        test_cycle_pid = 'CL-1'
        mock_get_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_create_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_get_tc_resp.to_dict.return_value = {'name': 'queens', 'pid': 'CL-2'}
        mock_create_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid}
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
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_get_tc_resp])
        mocker.patch('swagger_client.TestcycleApi.create_cycle', return_value=mock_create_tc_resp)

        # Setup
        zz = ZigZag(single_passing_xml, simple_json_config, TOKEN)
        zz.parse()
        zz.load_config()

        # Test
        response = zz.upload_test_results()
        assert int(job_id) == response

    def test_api_exception(self, single_passing_xml, simple_json_config, mocker):
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
        zz = ZigZag(single_passing_xml, simple_json_config, TOKEN)
        zz.parse()
        zz.load_config()

        # Test
        with pytest.raises(RuntimeError):
            zz.upload_test_results()

    def test_job_queue_failure(self, single_passing_xml, simple_json_config, mocker):
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
        zz = ZigZag(single_passing_xml, simple_json_config, TOKEN)
        zz.parse()
        zz.load_config()

        # Test
        with pytest.raises(RuntimeError):
            zz.upload_test_results()
