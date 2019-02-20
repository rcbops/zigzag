# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import os
import uuid
import pytest
import swagger_client
from copy import deepcopy
from swagger_client.rest import ApiException
from tests.helper.classes.zigzag_runner import ZigZagRunner


# ======================================================================================================================
# Public Fixtures: Meant to be consumed by tests
# ======================================================================================================================
@pytest.fixture(scope='session')
def qtest_env_vars():
    """Retrieve a dictionary of required environment variables for running integration tests.

    Returns:
        {str: obj}: A dictionary of environment variables. (Case sensitive)
    """

    env_vars = {}

    # noinspection PyUnusedLocal
    __tracebackhide__ = True
    try:
        env_vars['QTEST_API_TOKEN'] = os.environ['QTEST_API_TOKEN']
        env_vars['QTEST_SANDBOX_PROJECT_ID'] = int(os.environ['QTEST_SANDBOX_PROJECT_ID'])
    except KeyError:
        raise pytest.fail('Necessary environment variables not present!')

    return env_vars


# ======================================================================================================================
# Private Fixtures: Meant to be consumed by other fixtures
# ======================================================================================================================
# noinspection PyShadowingNames
@pytest.fixture(scope='session')
def _configure_test_environment(qtest_env_vars):
    """Configure the qTest project for testing.

    Returns:
        tuple(swagger_client.TestCycleResource, swagger_client.ModuleResource): A tuple containing the root test cycle
            and root requirement module to use for testing.

    Raises:
        RuntimeError: Failed to create or cleanup all qTest elements.
    """

    # Setup
    swagger_client.configuration.api_key['Authorization'] = qtest_env_vars['QTEST_API_TOKEN']
    project_id = qtest_env_vars['QTEST_SANDBOX_PROJECT_ID']
    test_cycle_api = swagger_client.TestcycleApi()
    module_api = swagger_client.ModuleApi()

    try:
        root_test_cycle = test_cycle_api.create_cycle(project_id=project_id,
                                                      parent_id=0,
                                                      parent_type='root',
                                                      body=swagger_client.TestCycleResource(name=str(uuid.uuid1())))
        root_req_module = module_api.create_module(project_id=project_id,
                                                   body=swagger_client.ModuleResource(name=str(uuid.uuid1())))
    except ApiException as e:
        raise RuntimeError("The qTest API reported an error!\n"
                           "Status code: {}\n"
                           "Reason: {}\n"
                           "Message: {}".format(e.status, e.reason, e.body))

    yield root_test_cycle, root_req_module

    # Teardown
    try:
        test_cycle_api.delete_cycle(project_id=project_id, test_cycle_id=root_test_cycle.id, force=True)
        module_api.delete_module(project_id=project_id, module_id=root_req_module.id, force=True)
    except ApiException as e:
        raise RuntimeError("The qTest API reported an error!\n"
                           "Status code: {}\n"
                           "Reason: {}\n"
                           "Message: {}".format(e.status, e.reason, e.body))


# noinspection PyShadowingNames
@pytest.fixture(scope='session')
def _zigzag_runner_factory(qtest_env_vars, _configure_test_environment, tmpdir_factory):
    """Instantiate an objects used to write ZigZag compliant JUnitXML files and execute ZigZag CLI.

    Returns:
        ZigZagRunner: Write ZigZag compliant JUnitXML files and execute ZigZag CLI.
    """

    zz_runners = []
    root_module_ids = []
    temp_dir = tmpdir_factory.mktemp('data')

    def _factory(junit_xml_file_name, config_file_path, global_properties_dict):
        """Instantiate an object used to write ZigZag compliant JUnitXML files and execute ZigZag CLI.

        Args:
            junit_xml_file_name (str): The name of the JUnitXML file. (Do not supply a file path!)
            config_file_path (str): The path to the config file to be used.
            global_properties_dict (dict): The global properties to be used to build the XML

        Returns:
            ZigZagRunner: Write ZigZag compliant JUnitXML files and execute ZigZag CLI.

        Raises:
            RuntimeError: Invalid value provided for the 'ci_environment' argument.
        """

        gpd = deepcopy(global_properties_dict)
        root_test_cycle, root_req_module = _configure_test_environment
        gpd['ZZ_INTEGRATION_TEST_CYCLE'] = root_test_cycle.name
        gpd['ZZ_INTEGRATION_PROJECT_ID'] = qtest_env_vars['QTEST_SANDBOX_PROJECT_ID']

        junit_xml_file_path = temp_dir.join(junit_xml_file_name).strpath
        runner = ZigZagRunner(qtest_env_vars['QTEST_API_TOKEN'],
                              qtest_env_vars['QTEST_SANDBOX_PROJECT_ID'],
                              root_test_cycle,
                              root_req_module,
                              junit_xml_file_path,
                              config_file_path,
                              gpd)
        zz_runners.append(runner)

        return runner

    yield _factory

    # Teardown
    module_api = swagger_client.ModuleApi()

    for zz_runner in zz_runners:
        for test in zz_runner.tests:
            if (test.qtest_root_module_id != 0) and (test.qtest_root_module_id not in root_module_ids):
                root_module_ids.append(test.qtest_root_module_id)

    for root_module_id in root_module_ids:
        try:
            module_api.delete_module(qtest_env_vars['QTEST_SANDBOX_PROJECT_ID'], root_module_id, force=True)
        except ApiException as e:
            if not (e.status == 404 and 'Module does not exist' in e.body):
                raise RuntimeError("The qTest API reported an error!\n"
                                   "Status code: {}\n"
                                   "Reason: {}\n"
                                   "Message: {}".format(e.status, e.reason, e.body))
