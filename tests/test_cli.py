#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from zigzag import cli
from click.testing import CliRunner


def test_cli_happy_path(single_passing_xml, mocker):
    """Verify that the CLI will process required arguments and environment variables. (All uploading of test
    results has been mocked)"""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    project_id = '12345'
    test_cycle = 'CL-1'

    runner = CliRunner()
    cli_arguments = [single_passing_xml, project_id, test_cycle]

    # Expectation
    job_id = '54321'

    # Mock
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)

    # Test
    result = runner.invoke(cli.main, args=cli_arguments, env=env_vars)
    assert 0 == result.exit_code
    assert 'Queue Job ID: {}'.format(job_id) in result.output
    assert 'Success!' in result.output


def test_cli_missing_api_token(single_passing_xml, mocker):
    """Verify that the CLI will gracefully fail if the expected API token env var is not set."""

    # Setup
    project_id = '12345'
    test_cycle = 'CL-1'

    runner = CliRunner()
    cli_arguments = [single_passing_xml, project_id, test_cycle]

    # Expectation
    job_id = '54321'
    error_msg_exp = 'The "QTEST_API_TOKEN" environment variable is not defined!'

    # Mock
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)

    # Test
    result = runner.invoke(cli.main, args=cli_arguments)
    assert 1 == result.exit_code
    assert error_msg_exp in result.output
    assert 'Failed!' in result.output


def test_cli_pprint_on_fail(missing_test_id_xml, mocker):
    """Verify that the CLI will allow the user to set the '--pprint-on-fail' flag for debug printing."""

    # Setup
    env_vars = {'QTEST_API_TOKEN': 'valid_token'}
    project_id = '12345'
    test_cycle = 'CL-1'
    job_id = '54321'

    runner = CliRunner()
    cli_arguments = [missing_test_id_xml, project_id, test_cycle, '--pprint-on-fail']

    # Expectations
    error_msg_exp = '---DEBUG XML PRETTY PRINT---'

    # Mock
    mock_queue_resp = mocker.Mock(state='IN_WAITING', id=job_id)
    mocker.patch('swagger_client.TestlogApi.submit_automation_test_logs_0', return_value=mock_queue_resp)

    # Test
    result = runner.invoke(cli.main, args=cli_arguments, env=env_vars)
    assert 1 == result.exit_code
    assert error_msg_exp in result.output
    assert 'Failed!' in result.output
