# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
import swagger_client
from zigzag.zigzag import ZigZag
from zigzag.utility_facade import UtilityFacade
from zigzag.module_hierarchy_facade import ModuleHierarchyFacade
from swagger_client.rest import ApiException
import requests
import json

# Shared variables
TOKEN = 'VALID_TOKEN'
PROJECT_ID = 12345
TEST_CYCLE = 'CL-1'

ASC_TESTSUITE_PROPS = {
    'RPC_RELEASE': 'foo',
    'JOB_NAME': 'bar',
    'MOLECULE_TEST_REPO': 'baz',
    'MOLECULE_SCENARIO_NAME': 'barf',
    'RPC_PRODUCT_RELEASE': 'queens'
}


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestModuleHierarchyFacade(object):
    """Tests for the ModuleHierarchyFacade"""

    def test_asc(self, mocker):
        """Validate when configured with asc as ci-environment"""

        # Mock
        zz = mocker.MagicMock()
        zz.ci_environment = 'asc'
        zz.utility_facade = UtilityFacade(zz)
        zz.testsuite_props = ASC_TESTSUITE_PROPS

        # Setup
        classname = 'tests.test_default'

        # Test
        mhf = ModuleHierarchyFacade(zz)
        mh = mhf.get_module_hierarchy(classname)
        assert mh == ['foo', 'bar', 'baz', 'barf', 'test_default']

    def test_mk8s_pr(self, mocker):
        """Validate when configured with mk8s as ci-environment"""

        # Mock
        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.utility_facade = UtilityFacade(zz)
        zz.testsuite_props = {
            'BRANCH_NAME': 'asc-123/master/stuff',
            'GIT_BRANCH': 'PR-123'
        }

        # Setup
        classname = 'tests.test_default'

        # Test
        mhf = ModuleHierarchyFacade(zz)
        assert mhf.get_module_hierarchy(classname) == ['PR-123', 'tests.test_default']

    def test_mk8s_branch_periodic(self, mocker):
        """Validate when configured with mk8s as ci-environment"""

        # Mock
        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.utility_facade = UtilityFacade(zz)
        zz.testsuite_props = {
            'BRANCH_NAME': 'master',
            'GIT_BRANCH': 'master'
        }

        # Setup
        classname = 'tests.test_default'

        # Test
        mhf = ModuleHierarchyFacade(zz)
        assert mhf.get_module_hierarchy(classname) == ['tests.test_default']

    def test_tempest(self, mocker):
        """Validate when configured with tempest as tool"""

        # Mock
        zz = mocker.MagicMock()
        zz.test_runner = 'tempest'
        zz.utility_facade = UtilityFacade(zz)

        # Setup
        classname = 'tests.test_default'

        # Test
        mhf = ModuleHierarchyFacade(zz)
        assert ['tests.test_default'] == mhf.get_module_hierarchy(classname)

    def test_bad_value(self, mocker):
        """Validate that if a bad value gets in we default to asc"""
        # Mock
        zz = mocker.MagicMock()
        zz.ci_environment = 'oops'
        zz.utility_facade = UtilityFacade(zz)
        zz.testsuite_props = ASC_TESTSUITE_PROPS

        # Setup
        classname = 'tests.test_default'

        # Test
        mhf = ModuleHierarchyFacade(zz)
        mh = mhf.get_module_hierarchy(classname)
        assert mh == ['foo', 'bar', 'baz', 'barf', 'test_default']


class TestDiscoverParentTestCycle(object):
    """Test cases for the 'discover_parent_test_cycle' function"""

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
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)

        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        mhf = ModuleHierarchyFacade(zz)

        # Test
        assert test_cycle_pid_exp == mhf.discover_root_test_cycle(test_cycle_name)

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
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)

        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])

        # Setup
        test_cycle_name = 'Queens'
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        mhf = ModuleHierarchyFacade(zz)

        # Test
        assert test_cycle_pid_exp == mhf.discover_root_test_cycle(test_cycle_name)

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
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)

        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_get_tc_resp])
        mocker.patch('swagger_client.TestcycleApi.create_cycle', return_value=mock_create_tc_resp)

        # Setup
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        mhf = ModuleHierarchyFacade(zz)

        # Test
        assert test_cycle_pid_exp == mhf.discover_root_test_cycle(test_cycle_name)

    def test_mismatched_test_cycle_name_case(self, single_passing_xml, mocker):
        """Verify that a mismatch in case does not cause a failure"""

        # Expectation
        test_cycle_pid_exp = 'CL-2'

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mock_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_tc_resp.to_dict.return_value = {'name': 'Queens', 'pid': test_cycle_pid_exp}
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)

        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_tc_resp])

        # Setup
        test_cycle_name = 'queens'
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        mhf = ModuleHierarchyFacade(zz)

        # Test
        assert test_cycle_pid_exp == mhf.discover_root_test_cycle(test_cycle_name)

    def test_failure_to_get_test_cycles(self, single_passing_xml, mocker):
        """Verify that API failure when retrieving test cycles is caught."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)
        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', side_effect=ApiException('Super duper failure!'))

        # Setup
        test_cycle_name = 'TestCycle1'
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        mhf = ModuleHierarchyFacade(zz)

        # Test
        with pytest.raises(RuntimeError):
            mhf.discover_root_test_cycle(test_cycle_name)

    def test_failure_to_create_test_cycle(self, single_passing_xml, mocker):
        """Verify that API failure when creating a test cycle is caught."""

        # Mock
        mock_field_resp = mocker.Mock(spec=swagger_client.FieldResource)
        mock_field_resp.id = 12345
        mock_field_resp.label = 'Failure Output'
        mock_get_tc_resp = mocker.Mock(spec=swagger_client.TestCycleResource)
        mock_get_tc_resp.to_dict.return_value = {'name': 'queens', 'pid': 'CL-2'}
        response = {'items': [{'name': 'insert name here', 'id': 12345}], 'total': 1}
        mock_post_response = mocker.Mock(spec=requests.Response)
        mock_post_response.text = json.dumps(response)

        mocker.patch('requests.post', return_value=mock_post_response)
        mocker.patch('swagger_client.FieldApi.get_fields', return_value=[mock_field_resp])
        mocker.patch('swagger_client.TestcycleApi.get_test_cycles', return_value=[mock_get_tc_resp])
        mocker.patch('swagger_client.TestcycleApi.create_cycle', side_effect=ApiException('Super duper failure!'))

        # Setup
        test_cycle_name = 'TestCycle1'
        zz = ZigZag(single_passing_xml, TOKEN, PROJECT_ID, TEST_CYCLE)
        mhf = ModuleHierarchyFacade(zz)

        # Test
        with pytest.raises(RuntimeError):
            mhf.discover_root_test_cycle(test_cycle_name)
