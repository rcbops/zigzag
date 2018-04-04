#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
from hashlib import md5
from zigzag import zigzag
from swagger_client.rest import ApiException


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

    def test_exceeds_max_file_size(self, flat_all_passing_xml, mocker):
        """Verify that XML files that exceed the max file size are rejected"""
        # Setup
        file_size = 52428801

        # Mock
        mocker.patch('os.path.getsize', return_value=file_size)

        # Test
        with pytest.raises(RuntimeError):
            zigzag._load_input_file(flat_all_passing_xml)


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
        test_log_exp = {'name': test_name,
                        'status': 'PASSED',
                        'module_names': ['Unknown'],
                        'automation_content': '1'}

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
        test_log_exp = {'name': test_name,
                        'status': 'FAILED',
                        'module_names': ['Unknown'],
                        'automation_content': '1'}

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
        test_log_exp = {'name': test_name,
                        'status': 'FAILED',
                        'module_names': ['Unknown'],
                        'automation_content': '1'}

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
        test_log_exp = {'name': test_name,
                        'status': 'SKIPPED',
                        'module_names': ['Unknown'],
                        'automation_content': '1'}

        # Test
        for exp in test_log_exp:
            assert test_log_exp[exp] == test_log_dict[exp]

    def test_missing_test_id_xml(self, missing_test_id_xml):
        """Verify that JUnitXML that is missing the 'test_id" test case property causes a RuntimeError."""

        # Setup
        junit_xml = zigzag._load_input_file(missing_test_id_xml)

        # Test
        with pytest.raises(RuntimeError):
            zigzag._generate_test_logs(junit_xml)

    def test_junit_xml_attachment(self, single_passing_xml):
        """Verify that a valid qTest 'AutomationTestLogResource' swagger model is generated with the raw JUnitXML
        file included as an attachment.
        """

        # Setup
        junit_xml = zigzag._load_input_file(single_passing_xml)
        # noinspection PyUnresolvedReferences
        test_log_dict = zigzag._generate_test_logs(junit_xml)[0].to_dict()

        # Expectation
        attachment_exp_name = 'junit.xml'
        attachment_exp_content_type = 'application/xml'
        attachment_exp_data_md5 = '45f29a8da0b0981e20c2c8562081280a'

        # Test
        assert attachment_exp_name == test_log_dict['attachments'][0]['name']
        assert attachment_exp_content_type == test_log_dict['attachments'][0]['content_type']
        assert attachment_exp_data_md5 == md5(test_log_dict['attachments'][0]['data'].encode('UTF-8')).hexdigest()


class TestGenerateAutoRequest(object):
    """Test cases for the '_generate_auto_request' function"""

    def test_mix_status(self, flat_mix_status_xml):
        """Verify that a valid qTest 'AutomationRequest' swagger model is generated from a JUnitXML file
        that contains multiple tests with different status results
        """

        # Setup
        test_cycle = 'CL-1'
        junit_xml = zigzag._load_input_file(flat_mix_status_xml)
        # noinspection PyUnresolvedReferences
        auto_req_dict = zigzag._generate_auto_request(junit_xml, test_cycle).to_dict()

        # Expectation
        prop_value = 'Unknown'
        test_logs_exp = [{'name': 'test_pass',
                          'status': 'PASSED',
                          'module_names': [prop_value],
                          'automation_content': '1'},
                         {'name': 'test_fail',
                          'status': 'FAILED',
                          'module_names': [prop_value],
                          'automation_content': '1'},
                         {'name': 'test_error',
                          'status': 'FAILED',
                          'module_names': [prop_value],
                          'automation_content': '1'},
                         {'name': 'test_skip',
                          'status': 'SKIPPED',
                          'module_names': [prop_value],
                          'automation_content': '1'}]

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
