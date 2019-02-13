# -*- coding: utf-8 -*-

"""Tests for verifying graceful handling of negative test scenarios."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import pytest
import swagger_client
from copy import deepcopy
from tests.helper.classes.zigzag_runner import ZigZagRunner


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
# noinspection PyShadowingNames
@pytest.fixture
def neg_invalid_api_token(qtest_env_vars,
                          _configure_test_environment,
                          tmpdir_factory,
                          asc_config_file,
                          asc_global_props):
    """ZigZag CLI runner configured with an invalid qTest API token.

    Returns:
        ZigZagRunner: Write ZigZag compliant JUnitXML files and execute ZigZag CLI.
    """

    # Setup
    temp_dir = tmpdir_factory.mktemp('data')
    agp = deepcopy(asc_global_props)
    root_test_cycle, root_req_module = _configure_test_environment
    junit_xml_file_path = temp_dir.join('neg_invalid_api_token.xml').strpath
    invalid_token = 'THIS IS NOT A VALID API TOKEN!!!!'

    agp['ZZ_INTEGRATION_TEST_CYCLE'] = root_test_cycle.name
    agp['ZZ_INTEGRATION_PROJECT_ID'] = qtest_env_vars['QTEST_SANDBOX_PROJECT_ID']

    zz_runner = ZigZagRunner(invalid_token,
                             qtest_env_vars['QTEST_SANDBOX_PROJECT_ID'],
                             root_test_cycle,
                             root_req_module,
                             junit_xml_file_path,
                             asc_config_file,
                             agp)

    zz_runner.add_test_case('passed')

    yield zz_runner

    # Teardown
    swagger_client.configuration.api_key['Authorization'] = qtest_env_vars['QTEST_API_TOKEN']


# noinspection PyShadowingNames
@pytest.fixture
def neg_invalid_project_id(qtest_env_vars,
                           _configure_test_environment,
                           tmpdir_factory,
                           asc_config_file,
                           asc_global_props):
    """ZigZag CLI runner configured with an invalid qTest project ID.

    Returns:
        ZigZagRunner: Write ZigZag compliant JUnitXML files and execute ZigZag CLI.
    """

    temp_dir = tmpdir_factory.mktemp('data')
    agp = deepcopy(asc_global_props)
    root_test_cycle, root_req_module = _configure_test_environment
    junit_xml_file_path = temp_dir.join('neg_invalid_project_id.xml').strpath
    invalid_project_id = 1234546789

    agp['ZZ_INTEGRATION_TEST_CYCLE'] = root_test_cycle.name
    agp['ZZ_INTEGRATION_PROJECT_ID'] = invalid_project_id

    zz_runner = ZigZagRunner(qtest_env_vars['QTEST_API_TOKEN'],
                             invalid_project_id,
                             root_test_cycle,
                             root_req_module,
                             junit_xml_file_path,
                             asc_config_file,
                             agp)

    zz_runner.add_test_case('passed')

    return zz_runner


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestNegativeScenarios(object):
    """Tests for verifying graceful handling of negative test scenarios."""

    # noinspection PyShadowingNames
    def test_invalid_api_token(self, neg_invalid_api_token):
        """Verify that ZigZag gracefully fails when an invalid API token is provided."""

        # Test
        with pytest.raises(RuntimeError) as e:
            neg_invalid_api_token.assert_invoke_zigzag()

        assert 'Reason: Unauthorized' in str(e.value)

    # noinspection PyShadowingNames
    def test_invalid_project_id(self, neg_invalid_project_id):
        """Verify that ZigZag gracefully fails when an invalid qTest project ID is specified."""

        # Test
        with pytest.raises(RuntimeError) as e:
            neg_invalid_project_id.assert_invoke_zigzag()

        assert 'Status code: 404' in str(e.value)
        assert 'Reason: Not Found' in str(e.value)
