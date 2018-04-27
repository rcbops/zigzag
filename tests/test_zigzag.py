#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import re
import pytest
from hashlib import md5
from zigzag import zigzag
from swagger_client.rest import ApiException

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


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestLoadingInputJunitXMLFile(object):
    """Test cases for the '_load_input_file' function"""

    def test_load_file_happy_path(self, flat_all_passing_xml):
        """Verify that a valid JUnitXML file can be loaded"""

        # Setup
        junit_xml = zigzag._load_input_file(flat_all_passing_xml)

        # Expectations
        root_tag_atribute_exp = {'errors': '0',
                                 'failures': '0',
                                 'name': 'pytest',
                                 'skips': '0',
                                 'tests': '5',
                                 'time': '1.664'}

        # Test
        assert root_tag_atribute_exp == junit_xml.attrib

    def test_invalid_file_path(self):
        """Verify that an invalid file path raises an exception"""

        # Test
        with pytest.raises(RuntimeError):
            zigzag._load_input_file('/path/does/not/exist')

    def test_invalid_xml_content(self, bad_xml):
        """Verify that invalid XML file content raises an exception"""

        # Test
        with pytest.raises(RuntimeError):
            zigzag._load_input_file(bad_xml)

    def test_missing_junit_xml_root(self, bad_junit_root):
        """Verify that XML files missing the expected JUnitXML root element raises an exception"""

        # Test
        with pytest.raises(RuntimeError):
            zigzag._load_input_file(bad_junit_root)

    def test_missing_build_url_xml(self, missing_build_url_xml):
        """Verify that JUnitXML that is missing the test suite 'BUILD_URL' property element causes a RuntimeError."""

        # Test
        with pytest.raises(RuntimeError):
            zigzag._load_input_file(missing_build_url_xml)

    def test_missing_testcase_properties_xml(self, missing_testcase_properties_xml):
        """Verify that JUnitXML that is missing the test case 'properties' element causes a RuntimeError."""

        # Test
        with pytest.raises(RuntimeError):
            zigzag._load_input_file(missing_testcase_properties_xml)

    def test_missing_test_id_xml(self, missing_test_id_xml):
        """Verify that JUnitXML that is missing the 'test_id' test case property causes a RuntimeError."""

        # Test
        with pytest.raises(RuntimeError):
            zigzag._load_input_file(missing_test_id_xml)

    def test_exceeds_max_file_size(self, flat_all_passing_xml, mocker):
        """Verify that XML files that exceed the max file size are rejected"""
        # Setup
        file_size = 52428801

        # Mock
        mocker.patch('os.path.getsize', return_value=file_size)

        # Test
        with pytest.raises(RuntimeError):
            zigzag._load_input_file(flat_all_passing_xml)

    def test_schema_violation_with_pprint_on_fail(self, missing_test_id_xml):
        """Verify that JUnitXML that violates the schema with 'pprint_on_fail' enabled with emit an error message with
        the XML pretty printed in the error message."""

        # Expectations
        error_msg_exp = '---DEBUG XML PRETTY PRINT---'

        # Test
        try:
            zigzag._load_input_file(missing_test_id_xml, pprint_on_fail=True)
        except RuntimeError as e:
            assert error_msg_exp in str(e)


# noinspection PyUnresolvedReferences
class TestGenerateTestLogs(object):
    """Test cases for the '_generate_test_logs' function"""

    def test_pass(self, single_passing_xml):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a single passing test.
        """

        # Setup
        junit_xml = zigzag._load_input_file(single_passing_xml)
        # noinspection PyUnresolvedReferences
        test_log_dict = zigzag._generate_test_logs(junit_xml)[0].to_dict()

        # Expectation
        test_name = 'test_pass'
        test_log_exp = pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': test_name, 'status': 'PASSED'})

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_fail(self, single_fail_xml):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a single failing test
        """

        # Setup
        junit_xml = zigzag._load_input_file(single_fail_xml)
        # noinspection PyUnresolvedReferences
        test_log_dict = zigzag._generate_test_logs(junit_xml)[0].to_dict()

        # Expectation
        test_name = 'test_fail'
        test_log_exp = pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': test_name, 'status': 'FAILED'})

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_error(self, single_error_xml):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a single erroring test
        """

        # Setup
        junit_xml = zigzag._load_input_file(single_error_xml)
        # noinspection PyUnresolvedReferences
        test_log_dict = zigzag._generate_test_logs(junit_xml)[0].to_dict()

        # Expectation
        test_name = 'test_error'
        test_log_exp = pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': test_name, 'status': 'FAILED'})

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_skip(self, single_skip_xml):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a single skipping test
        """

        # Setup
        junit_xml = zigzag._load_input_file(single_skip_xml)
        # noinspection PyUnresolvedReferences
        test_log_dict = zigzag._generate_test_logs(junit_xml)[0].to_dict()

        # Expectation
        test_name = 'test_skip'
        test_log_exp = pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': test_name, 'status': 'SKIPPED'})

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_suite_with_tests(self, suite_all_passing_xml):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a multiple passing tests that were grouped within a Python class.
        """

        # Setup
        junit_xml = zigzag._load_input_file(suite_all_passing_xml)
        # noinspection PyUnresolvedReferences
        test_logs = zigzag._generate_test_logs(junit_xml)

        # Expectation
        shared_test_log_suite_exp = {'status': 'PASSED',
                                     'module_names': ['RPC_RELEASE',
                                                      'JOB_NAME',
                                                      'MOLECULE_TEST_REPO',
                                                      'MOLECULE_SCENARIO_NAME',
                                                      'test_default',
                                                      'TestSuite']}

        test_logs_exp = [pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP,
                                                    shared_test_log_suite_exp,
                                                    {'name': 'test_pass{}'.format(x)})
                         for x in range(1, 6)]

        # Test
        for x in range(len(test_logs)):
            for key in test_logs_exp[x]:
                assert test_logs_exp[x][key] == test_logs[x].to_dict()[key]

    def test_junit_xml_attachment(self, single_passing_xml):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated with the raw JUnitXML
        file included as an attachment.
        """

        # Setup
        junit_xml = zigzag._load_input_file(single_passing_xml)
        # noinspection PyUnresolvedReferences
        test_log_dict = zigzag._generate_test_logs(junit_xml)[0].to_dict()

        # Expectation
        attachment_exp_name_regex = re.compile(r'^junit_.+\.xml$')
        attachment_exp_content_type = 'application/xml'
        attachment_exp_data_md5 = '17a3778912a8bf149eaf13311e82b85e'

        # Test
        assert attachment_exp_name_regex.match(test_log_dict['attachments'][0]['name']) is not None
        assert attachment_exp_content_type == test_log_dict['attachments'][0]['content_type']
        assert attachment_exp_data_md5 == md5(test_log_dict['attachments'][0]['data'].encode('UTF-8')).hexdigest()

    def test_classname_containing_dashes(self, classname_with_dashes_xml):
        """Verify that JUnitXML that has a 'classname' containing dashes (captured from the py.test filename) is
        validated correctly.
        """

        # Setup
        junit_xml = zigzag._load_input_file(classname_with_dashes_xml)
        # noinspection PyUnresolvedReferences
        test_log_dict = zigzag._generate_test_logs(junit_xml)[0].to_dict()

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

    def test_invalid_classname(self, invalid_classname_xml):
        """Verify that JUnitXML that has an invalid 'classname' attribute for a testcase raises a RuntimeError."""

        # Setup
        junit_xml = zigzag._load_input_file(invalid_classname_xml)

        # Test
        with pytest.raises(RuntimeError):
            zigzag._generate_test_logs(junit_xml)


# noinspection PyUnresolvedReferences
class TestGenerateAutoRequest(object):
    """Test cases for the '_generate_auto_request' function"""

    def test_mix_status(self, flat_mix_status_xml):
        """Verify that a valid qTest 'AutomationRequest' swagger model is generated from a JUnitXML file
        that contains multiple tests with different status results
        """

        # Setup
        test_cycle = 'CL-1'
        junit_xml = zigzag._load_input_file(flat_mix_status_xml)
        auto_req_dict = zigzag._generate_auto_request(junit_xml, test_cycle).to_dict()

        # Expectation
        test_logs_exp = [pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': 'test_pass', 'status': 'PASSED'}),
                         pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': 'test_fail', 'status': 'FAILED'}),
                         pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': 'test_error', 'status': 'FAILED'}),
                         pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': 'test_skip', 'status': 'SKIPPED'})]

        # Test
        for x in range(len(auto_req_dict['test_logs'])):
            for key in test_logs_exp[x]:
                assert test_logs_exp[x][key] == auto_req_dict['test_logs'][x][key]


class TestUploadTestResults(object):
    """Test cases for the 'upload_test_results' function"""

    def test_happy_path(self, single_passing_xml, mocker):
        """Verify that the function can upload results from a JUnitXML file that contains a single passing test"""

        # Setup
        api_token = 'valid_token'
        project_id = 12345
        test_cycle = 'CL-1'

        # Expectation
        job_id = '54321'

        # Mock
        mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
        mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)

        # Test
        response = zigzag.upload_test_results(single_passing_xml, api_token, project_id, test_cycle)
        assert int(job_id) == response

    def test_api_exception(self, single_passing_xml, mocker):
        """Verify that the function fails gracefully if the API endpoint reports an API exception"""

        # Setup
        api_token = 'valid_token'
        project_id = 12345
        test_cycle = 'CL-1'

        # Mock
        mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0',
                     side_effect=ApiException('Super duper failure!'))

        # Test
        with pytest.raises(RuntimeError):
            zigzag.upload_test_results(single_passing_xml, api_token, project_id, test_cycle)

    def test_job_queue_failure(self, single_passing_xml, mocker):
        """Verify that the function fails gracefully if the job queue reports a failure"""

        # Setup
        api_token = 'valid_token'
        project_id = 12345
        test_cycle = 'CL-1'

        # Mock
        mock_queue_resp = mocker.Mock(state='FAILED')
        mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)

        # Test
        with pytest.raises(RuntimeError):
            zigzag.upload_test_results(single_passing_xml, api_token, project_id, test_cycle)
