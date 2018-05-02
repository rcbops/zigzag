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
class TestLoadingInputJunitXMLFile(object):
    """Test cases for the '_load_input_file' function"""

    def test_load_file_happy_path(self, flat_all_passing_xml, mocker):
        """Verify that a valid JUnitXML file can be loaded"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

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
class TestGenerateTestLogs(object):
    """Test cases for the '_generate_test_logs' function"""

    def test_pass(self, single_passing_xml, mocker):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a single passing test.
        """

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log_dict = zz._generate_test_logs()[0].to_dict()

        # Expectation
        test_name = 'test_pass'
        test_log_exp = pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': test_name, 'status': 'PASSED'})

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_fail(self, single_fail_xml, mocker):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a single failing test
        """

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(single_fail_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log_dict = zz._generate_test_logs()[0].to_dict()

        # Expectation
        test_name = 'test_fail'
        test_log_exp = pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': test_name, 'status': 'FAILED'})

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_error(self, single_error_xml, mocker):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a single erroring test
        """

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(single_error_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log_dict = zz._generate_test_logs()[0].to_dict()

        # Expectation
        test_name = 'test_error'
        test_log_exp = pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': test_name, 'status': 'FAILED'})

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_skip(self, single_skip_xml, mocker):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a single skipping test
        """

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(single_skip_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log_dict = zz._generate_test_logs()[0].to_dict()

        # Expectation
        test_name = 'test_skip'
        test_log_exp = pytest.helpers.merge_dicts(SHARED_TEST_LOG_EXP, {'name': test_name, 'status': 'SKIPPED'})

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_suite_with_tests(self, suite_all_passing_xml, mocker):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated from a JUnitXML file
        that contains a multiple passing tests that were grouped within a Python class.
        """

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(suite_all_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_logs = zz._generate_test_logs()

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

    def test_junit_xml_attachment(self, single_passing_xml, mocker):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated with the raw JUnitXML
        file included as an attachment.
        """

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log_dict = zz._generate_test_logs()[0].to_dict()

        # Expectation
        attachment_exp_name_regex = re.compile(r'^junit_.+\.xml$')
        attachment_exp_content_type = 'application/xml'
        attachment_exp_data_md5 = '17a3778912a8bf149eaf13311e82b85e'

        # Test
        assert attachment_exp_name_regex.match(test_log_dict['attachments'][0]['name']) is not None
        assert attachment_exp_content_type == test_log_dict['attachments'][0]['content_type']
        assert attachment_exp_data_md5 == md5(test_log_dict['attachments'][0]['data'].encode('UTF-8')).hexdigest()

    def test_classname_containing_dashes(self, classname_with_dashes_xml, mocker):
        """Verify that JUnitXML that has a 'classname' containing dashes (captured from the py.test filename) is
        validated correctly.
        """

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(classname_with_dashes_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        # noinspection PyUnresolvedReferences
        test_log_dict = zz._generate_test_logs()[0].to_dict()

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

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(invalid_classname_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        with pytest.raises(RuntimeError):
            zz._generate_test_logs()


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
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

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
                assert test_logs_exp[x][key] == auto_req_dict['test_logs'][x][key]


class TestDiscoverParentTestCycle(object):
    """Test cases for the '_discover_parent_test_cycle' function"""

    def test_discover_existing_test_cycle(self, single_passing_xml, mocker):
        """Verify that the PID for an existing test cycle can be discovered."""

        # Expectation
        test_cycle_pid_exp = 'CL-1'

        # Mock
        test_cycle_name = 'TestCycle1'
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mock_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid_exp}

        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        assert test_cycle_pid_exp == zz._discover_parent_test_cycle(test_cycle_name)

    def test_discover_existing_test_cycle_with_case_change(self, single_passing_xml, mocker):
        """Verify that the PID for an existing test cycle can be discovered when using a different case for search."""

        # Expectation
        test_cycle_pid_exp = 'CL-2'

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mock_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_tc_resp.to_dict.return_value = {'name': 'queens', 'pid': test_cycle_pid_exp}

        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])

        # Setup
        test_cycle_name = 'Queens'
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        assert test_cycle_pid_exp == zz._discover_parent_test_cycle(test_cycle_name)

    def test_create_test_cycle(self, single_passing_xml, mocker):
        """Verify that a new test cycle will be created when the desired cycle name cannot be found."""

        # Setup
        test_cycle_name = 'Buttons'

        # Expectation
        test_cycle_pid_exp = 'CL-3'

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mock_get_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_create_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_get_tc_resp.to_dict.return_value = {'name': 'queens', 'pid': 'CL-2'}
        mock_create_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid_exp}

        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_get_tc_resp])
        mocker.patch('swagger_client.TestcycleApi.create_cycle', return_value=mock_create_tc_resp)

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        assert test_cycle_pid_exp == zz._discover_parent_test_cycle(test_cycle_name)

    def test_failure_to_get_test_cycles(self, single_passing_xml, mocker):
        """Verify that API failure when retrieving test cycles is caught."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', side_effect=ApiException('Super duper failure!'))

        # Setup
        test_cycle_name = 'TestCycle1'
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        with pytest.raises(RuntimeError):
            zz._discover_parent_test_cycle(test_cycle_name)

    def test_failure_to_create_test_cycle(self, single_passing_xml, mocker):
        """Verify that API failure when creating a test cycle is caught."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mock_get_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_get_tc_resp.to_dict.return_value = {'name': 'queens', 'pid': 'CL-2'}

        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_get_tc_resp])
        mocker.patch('swagger_client.TestcycleApi.create_cycle', side_effect=ApiException('Super duper failure!'))

        # Setup
        test_cycle_name = 'TestCycle1'
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        with pytest.raises(RuntimeError):
            zz._discover_parent_test_cycle(test_cycle_name)


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
        mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

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
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0',
                     side_effect=ApiException('Super duper failure!'))

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
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mock_queue_resp = mocker.Mock(state='FAILED')
        mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

        # Test
        with pytest.raises(RuntimeError):
            zz.upload_test_results()


class TestFindCustomFieldIdByLabel(object):
    """Test cases for the 'find_custom_field_id_by_label' function"""

    def test_a_failure(self, single_fail_xml, mocker):
        """Verify that when a test fails we attach a Failure Output field"""
        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(single_fail_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        only_property = zz._generate_test_logs()[0].to_dict()['properties'][0]

        assert all([x in only_property for x in ['field_id', 'field_value']])
        assert only_property['field_id'] == mock_field_resp.id
        assert only_property['field_value'] == 'assert False'

    def test_no_failures(self, single_passing_xml, mocker):
        """Verify that when a test passes we do not attach a Failure Output field"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        properties = zz._generate_test_logs()[0].to_dict()['properties']

        assert not properties

    def test_an_error(self, single_error_xml, mocker):
        """Verify that when a test errors we attach a Failure Output field"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        # Setup
        zz = ZigZag(single_error_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        only_property = zz._generate_test_logs()[0].to_dict()['properties'][0]

        assert all([x in only_property for x in ['field_id', 'field_value']])
        assert only_property['field_id'] == mock_field_resp.id
        assert only_property['field_value'] == 'test setup failure'

    def test_api_failure(self, single_passing_xml, mocker):
        """Verify that an ApiException will cause a RuntimeError"""

        # Mock
        mocker.patch('swagger_client.FieldApi.get_fields', side_effect=ApiException('Super duper failure!'))

        # Test
        with pytest.raises(RuntimeError):
            ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)

    def test_field_not_configured(self, single_error_xml, mocker):
        """Verify properties is empty if field is not configured"""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'This is not the field you are looking for'
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])

        zz = ZigZag(single_error_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        empty_properties = zz._generate_test_logs()[0].to_dict()['properties']
        assert not empty_properties
