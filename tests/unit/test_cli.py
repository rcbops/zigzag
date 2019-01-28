# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import swagger_client
from zigzag import cli
from click.testing import CliRunner
import requests
import json


def test_cli_happy_path(single_passing_xml, simple_json_config, mocker):
    """Verify that the CLI will process required arguments and environment variables. (All uploading of test
    results has been mocked)"""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    test_cycle_name = 'pike'
    test_cycle_pid = 'CL-1'

    runner = CliRunner()
    cli_arguments = (simple_json_config, single_passing_xml)

    # Expectation
    job_id = '54321'

    # Mock
    response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
    mock_post_response = mocker.Mock(spec=requests.Response)
    mock_post_response.text = json.dumps(response)
    mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
    mock_field_resp.id = 12345
    mock_field_resp.label = 'Failure Output'
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
    mock_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
    mock_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid}
    mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)

    mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)
    mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])
    mocker.patch('requests.post', return_value=mock_post_response)
    mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

    # Test
    result = runner.invoke(cli.main, args=cli_arguments, env=env_vars)
    assert 0 == result.exit_code
    assert 'Queue Job ID: {}'.format(job_id) in result.output
    assert 'Success!' in result.output


def test_cli_missing_api_token(single_passing_xml, simple_json_config, mocker):
    """Verify that the CLI will gracefully fail if the expected API token env var is not set."""

    # Setup
    test_cycle_name = 'RPC_PRODUCT_RELEASE'
    test_cycle_pid = 'CL-1'

    runner = CliRunner()
    cli_arguments = (simple_json_config, single_passing_xml)

    # Expectation
    job_id = '54321'
    error_msg_exp = 'The "QTEST_API_TOKEN" environment variable is not defined!'

    # Mock
    mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
    mock_field_resp.id = 12345
    mock_field_resp.label = 'Failure Output'
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
    mock_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
    mock_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid}

    mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)
    mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])

    # Test
    result = runner.invoke(cli.main, args=cli_arguments)
    assert 1 == result.exit_code
    assert error_msg_exp in result.output
    assert 'Failed!' in result.output


def test_specify_test_cycle(single_passing_xml, simple_json_config, mocker):
    """Verify that the CLI will allow the user to set the '--pprint-on-fail' flag for debug printing."""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    test_cycle_pid = 'CL-1'
    test_cycle_name = 'RPC_PRODUCT_RELEASE'

    runner = CliRunner()
    cli_arguments = (simple_json_config, single_passing_xml)

    # Expectation
    job_id = '54321'

    # Mock
    response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
    mock_post_response = mocker.Mock(spec=requests.Response)
    mock_post_response.text = json.dumps(response)
    mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
    mock_field_resp.id = 12345
    mock_field_resp.label = 'Failure Output'
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
    mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)
    mock_get_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
    mock_create_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
    mock_get_tc_resp.to_dict.return_value = {'name': 'queens', 'pid': 'CL-2'}
    mock_create_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid}

    mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)
    mocker.patch('requests.post', return_value=mock_post_response)
    mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])
    mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_get_tc_resp])
    mocker.patch('swagger_client.TestcycleApi.create_cycle', return_value=mock_create_tc_resp)
# Test
    result = runner.invoke(cli.main, args=cli_arguments, env=env_vars)
    assert 0 == result.exit_code
    assert 'Queue Job ID: {}'.format(job_id) in result.output
    assert 'Success!' in result.output


def test_cli_pprint_on_fail(missing_test_id_xml, simple_json_config, mocker):
    """Verify that the CLI will allow the user to set the '--pprint-on-fail' flag for debug printing."""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    job_id = '54321'
    test_cycle_name = 'RPC_PRODUCT_RELEASE'
    test_cycle_pid = 'CL-1'

    runner = CliRunner()
    cli_arguments = (simple_json_config, missing_test_id_xml, "--pprint-on-fail")

    # Expectations
    error_msg_exp = '---DEBUG XML PRETTY PRINT---'

    # Mock
    mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
    mock_field_resp.id = 12345
    mock_field_resp.label = 'Failure Output'
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
    mock_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
    mock_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid}

    mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)
    mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])

    # Test
    result = runner.invoke(cli.main, args=cli_arguments, env=env_vars)
    assert 1 == result.exit_code
    assert error_msg_exp in result.output
    assert 'Failed!' in result.output


def test_cli_config_option(simple_json_config, single_passing_xml, mocker):
    """Verify that the CLI will allow the user to set the '--zigzag_config_file' option."""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    test_cycle_name = 'pike'
    test_cycle_pid = 'CL-1'

    runner = CliRunner()
    cli_arguments = (simple_json_config, single_passing_xml)

    # Expectation
    job_id = '54321'

    # Mock
    response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
    mock_post_response = mocker.Mock(spec=requests.Response)
    mock_post_response.text = json.dumps(response)
    mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
    mock_field_resp.id = 12345
    mock_field_resp.label = 'Failure Output'
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
    mock_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
    mock_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid}
    mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)

    mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)
    mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])
    mocker.patch('requests.post', return_value=mock_post_response)
    mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

    # Test
    result = runner.invoke(cli.main, args=cli_arguments, env=env_vars)
    assert 0 == result.exit_code
    assert 'Queue Job ID: {}'.format(job_id) in result.output
    assert 'Success!' in result.output


def test_cli_malformed_config(invalid_json_config, single_passing_xml, mocker):
    """Ensure that when given an invalid config, that we fail with a 'not valid JSON' error."""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    test_cycle_name = 'pike'
    test_cycle_pid = 'CL-1'

    runner = CliRunner()
    cli_arguments = (invalid_json_config, single_passing_xml)

    # Expectation
    job_id = '54321'

    # Mock
    response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
    mock_post_response = mocker.Mock(spec=requests.Response)
    mock_post_response.text = json.dumps(response)
    mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
    mock_field_resp.id = 12345
    mock_field_resp.label = 'Failure Output'
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
    mock_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
    mock_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid}
    mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)

    mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)
    mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])
    mocker.patch('requests.post', return_value=mock_post_response)
    mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

    # Test
    result = runner.invoke(cli.main, args=cli_arguments, env=env_vars)
    assert 'config file is not valid JSON' in result.output


def test_cli_missing_config(simple_json_config, single_passing_xml, mocker):
    """Ensure that config file option is required."""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    test_cycle_name = 'pike'
    test_cycle_pid = 'CL-1'

    runner = CliRunner()
    cli_arguments = (simple_json_config + '_invalid', single_passing_xml)

    # Expectation
    job_id = '54321'

    # Mock
    response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
    mock_post_response = mocker.Mock(spec=requests.Response)
    mock_post_response.text = json.dumps(response)
    mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
    mock_field_resp.id = 12345
    mock_field_resp.label = 'Failure Output'
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
    mock_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
    mock_tc_resp.to_dict.return_value = {'name': test_cycle_name, 'pid': test_cycle_pid}
    mock_link_response = mocker.Mock(spec=swagger_client.LinkedArtifactContainer)

    mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)
    mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])
    mocker.patch('requests.post', return_value=mock_post_response)
    mocker.patch('swagger_client.ObjectlinkApi.link_artifacts', return_value=[mock_link_response])

    # Test
    result = runner.invoke(cli.main, args=cli_arguments, env=env_vars)
    assert 'Error: Invalid value for "ZIGZAG_CONFIG_FILE"' in result.output
    assert 'conf.json_invalid" does not exist.\n' in result.output
