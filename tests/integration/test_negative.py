# -*- coding: utf-8 -*-

"""Tests for verifying graceful handling of negative test scenarios."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
import swagger_client
from conftest import ZigZagRunner


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
# noinspection PyShadowingNames
@pytest.fixture(scope='session')
def neg_invalid_project_id(qtest_env_vars, _configure_test_environment, tmpdir_factory):
    """ZigZag CLI runner configured with an invalid qTest project ID.

    Returns:
        ZigZagRunner: Write ZigZag compliant JUnitXML files and execute ZigZag CLI.
    """

    temp_dir = tmpdir_factory.mktemp('data')
    root_test_cycle, root_req_module = _configure_test_environment
    junit_xml_file_path = temp_dir.join('neg_invalid_project_id.xml').strpath
    invalid_project_id = 1234546789
    ci_environment = 'asc'

    return ZigZagRunner(qtest_env_vars['QTEST_API_TOKEN'],
                        invalid_project_id,
                        root_test_cycle,
                        root_req_module,
                        junit_xml_file_path,
                        ci_environment)


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestNegativeScenarios(object):
    """Tests for verifying graceful handling of negative test scenarios."""

    def test_invalid_api_token(self, qtest_env_vars, _configure_test_environment, tmpdir_factory):
        """Verify that ZigZag gracefully fails when an invalid API token is provided.

        Note: This test is brittle by nature because of how the swagger_client handles the API token for authorization.
        If this tests fails to reach "Teardown" then it will trigger cascading failures.

        But why? Well, because of how we control the fixture teardown for the non-negative scenarios it is impossible
        to inject a bad token through the current fixture pattern. Therefore, we hand roll everything inside this test
        to make sure we set the swagger_client back to an authorized token.
        """

        # Setup
        temp_dir = tmpdir_factory.mktemp('data')
        root_test_cycle, root_req_module = _configure_test_environment
        junit_xml_file_path = temp_dir.join('neg_invalid_api_token.xml').strpath
        invalid_token = 'THIS IS NOT A VALID API TOKEN!!!!'
        ci_environment = 'asc'

        zz_runner = ZigZagRunner(invalid_token,
                                 qtest_env_vars['QTEST_SANDBOX_PROJECT_ID'],
                                 root_test_cycle,
                                 root_req_module,
                                 junit_xml_file_path,
                                 ci_environment)

        zz_runner.add_test_case('passed')

        # Test
        with pytest.raises(RuntimeError) as e:
            zz_runner.assert_invoke_zigzag()

        assert 'Reason: Unauthorized' in e.value.message

        # Teardown
        swagger_client.configuration.api_key['Authorization'] = qtest_env_vars['QTEST_API_TOKEN']

    # noinspection PyShadowingNames
    def test_invalid_project_id(self, neg_invalid_project_id):
        """Verify that ZigZag gracefully fails when an invalid qTest project ID is specified."""

        # Setup
        neg_invalid_project_id.add_test_case('passed')

        # Test
        with pytest.raises(RuntimeError) as e:
            neg_invalid_project_id.assert_invoke_zigzag()

        assert 'Status code: 404' in e.value.message
        assert 'Reason: Not Found' in e.value.message
