#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import swagger_client
from zigzag import cli
from click.testing import CliRunner


def test_cli_happy_path(single_passing_xml, mocker):
    """Verify that the CLI will process required arguments and environment variables. (All uploading of test
    results has been mocked)"""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    project_id = '12345'
    test_cycle_name = 'RPC_PRODUCT_RELEASE'
    test_cycle_pid = 'CL-1'

    runner = CliRunner()
    cli_arguments = [single_passing_xml, project_id]

    # Expectation
    job_id = '54321'

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
    assert 0 == result.exit_code
    assert 'Queue Job ID: {}'.format(job_id) in result.output
    assert 'Success!' in result.output


def test_cli_missing_api_token(single_passing_xml, mocker):
    """Verify that the CLI will gracefully fail if the expected API token env var is not set."""

    # Setup
    project_id = '12345'
    test_cycle_name = 'RPC_PRODUCT_RELEASE'
    test_cycle_pid = 'CL-1'

    runner = CliRunner()
    cli_arguments = [single_passing_xml, project_id]

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


def test_specify_test_cycle(single_passing_xml, mocker):
    """Verify that the CLI will allow the user to set the '--pprint-on-fail' flag for debug printing."""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    project_id = '12345'
    test_cycle_pid = 'CL-1'

    runner = CliRunner()
    cli_arguments = [single_passing_xml, project_id, '--qtest-test-cycle={}'.format(test_cycle_pid)]

    # Expectation
    job_id = '54321'

    # Mock
    mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
    mock_field_resp.id = 12345
    mock_field_resp.label = 'Failure Output'
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)

    mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)

    # Test
    result = runner.invoke(cli.main, args=cli_arguments, env=env_vars)
    assert 0 == result.exit_code
    assert 'Queue Job ID: {}'.format(job_id) in result.output
    assert 'Success!' in result.output


def test_cli_pprint_on_fail(missing_test_id_xml, mocker):
    """Verify that the CLI will allow the user to set the '--pprint-on-fail' flag for debug printing."""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    project_id = '12345'
    job_id = '54321'
    test_cycle_name = 'RPC_PRODUCT_RELEASE'
    test_cycle_pid = 'CL-1'

    runner = CliRunner()
    cli_arguments = [missing_test_id_xml, project_id, '--pprint-on-fail']

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
