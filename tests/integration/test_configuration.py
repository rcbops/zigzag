# -*- coding: utf-8 -*-

"""Test supported configurations of zigzag."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
from zigzag.zigzag_config import ZigZagConfigError
from tests.helper.classes.zigzag_runner import ZigZagRunner


# ======================================================================================================================
# Fixtures
# ======================================================================================================================

@pytest.fixture(scope='session')
def bad_hierarchy_config_file(tmpdir_factory):
    """A configuration with a module_hierarchy of the wrong type
    """

    filename = tmpdir_factory.mktemp('data').join('config_file.json').strpath
    config_json = \
        """{
              "zigzag": {
                "test_cycle": "{{ ZZ_INTEGRATION_TEST_CYCLE }}",
                "project_id": "{{ ZZ_INTEGRATION_PROJECT_ID }}",
                "module_hierarchy": "node1, node2"
              }
            }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def no_test_cycle_config(tmpdir_factory):
    """A configuration missing the test_cycle config
    """

    filename = tmpdir_factory.mktemp('data').join('config_file.json').strpath
    config_json = \
        """{
              "zigzag": {
                "project_id": "{{ ZZ_INTEGRATION_PROJECT_ID }}",
                "module_hierarchy": [
                  "{{ RPC_PRODUCT_RELEASE }}",
                  "{{ RPC_RELEASE }}",
                  "{{ JOB_NAME }}",
                  "{{ MOLECULE_TEST_REPO }}",
                  "{{ zz_testcase_class }}"
                ]
              }
            }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def no_module_hierarchy_config(tmpdir_factory):
    """A configuration missing the test_cycle config
    """

    filename = tmpdir_factory.mktemp('data').join('config_file.json').strpath
    config_json = \
        """{
              "zigzag": {
                "test_cycle": "{{ ZZ_INTEGRATION_TEST_CYCLE }}",
                "project_id": "{{ ZZ_INTEGRATION_PROJECT_ID }}"
              }
            }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def no_project_id_config(tmpdir_factory):
    """A configuration missing the test_cycle config
    """

    filename = tmpdir_factory.mktemp('data').join('config_file.json').strpath
    config_json = \
        """{
              "zigzag": {
                "test_cycle": "{{ ZZ_INTEGRATION_TEST_CYCLE }}",
                "module_hierarchy": [
                  "{{ RPC_PRODUCT_RELEASE }}",
                  "{{ RPC_RELEASE }}",
                  "{{ JOB_NAME }}",
                  "{{ MOLECULE_TEST_REPO }}",
                  "{{ zz_testcase_class }}"
                ]
              }
            }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def required_configs(tmpdir_factory):
    """A configuration with required configs
    used to test when properties evaluate to empty things
    """

    filename = tmpdir_factory.mktemp('data').join('config_file.json').strpath
    config_json = \
        """{
              "zigzag": {
                "test_cycle": "{{ ZZ_INTEGRATION_TEST_CYCLE }}",
                "project_id": "{{ ZZ_INTEGRATION_PROJECT_ID }}",
                "module_hierarchy": [
                  "{{ ZZ_MODULE_HIERARCHY_ONE }}",
                  "{{ ZZ_MODULE_HIERARCHY_TWO }}"
                ]
              }
            }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def custom_hierarchy_config_file(tmpdir_factory):
    """A config for zigzag that interpolates a value from the execution environment

    Returns:
        str : a path to a config file
    """

    filename = tmpdir_factory.mktemp('data').join('config_file.json').strpath
    config_json = \
        """{
              "zigzag": {
                "test_cycle": "{{ ZZ_INTEGRATION_TEST_CYCLE }}",
                "project_id": "{{ ZZ_INTEGRATION_PROJECT_ID }}",
                "module_hierarchy": [
                  "{{ zz_testcase_class }}"
                ]
              }
            }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def computed_hierarchy_config_file_falsey(tmpdir_factory):
    """A config for zigzag that computes an interpolated value based on a false condition

    Returns:
        str : a path to a config file
    """

    filename = tmpdir_factory.mktemp('data').join('config_file.json').strpath
    config_json = \
        """{
              "zigzag": {
                "test_cycle": "{{ ZZ_INTEGRATION_TEST_CYCLE }}",
                "project_id": "{{ ZZ_INTEGRATION_PROJECT_ID }}",
                "module_hierarchy": [
                  "{{ 'foo' if False else 'bar' }}"
                ]
              }
            }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def computed_hierarchy_config_file_truthy(tmpdir_factory):
    """A config for zigzag that computes an interpolated value based on a true condition

    Returns:
        str : a path to a config file
    """

    filename = tmpdir_factory.mktemp('data').join('config_file.json').strpath
    config_json = \
        """{
              "zigzag": {
                "test_cycle": "{{ ZZ_INTEGRATION_TEST_CYCLE }}",
                "project_id": "{{ ZZ_INTEGRATION_PROJECT_ID }}",
                "module_hierarchy": [
                  "{{ 'foo' if True else 'bar' }}"
                ]
              }
            }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestConfig(object):
    # noinspection PyUnresolvedReferences
    def test_publish_single_passing_test_with_interpolated_mod_hierarchy(self,
                                                                         _zigzag_runner_factory,
                                                                         custom_hierarchy_config_file):
        """ Verify that values in the zigzag execution environment can be interpolated into
            a zigzag config
        """

        zz_runner = _zigzag_runner_factory('junit.xml', custom_hierarchy_config_file, {})
        zz_runner.add_test_case('passed')
        zz_runner.assert_invoke_zigzag()
        test = zz_runner.tests[0]
        qtest_parent_test_cycle_name = test.qtest_parent_test_cycles[0].name

        # Expectations
        parent_test_cycle_name_exp = 'tests.test_default'

        # Test
        assert parent_test_cycle_name_exp == qtest_parent_test_cycle_name

    # noinspection PyUnresolvedReferences
    def test_publish_single_passing_test_with_computed_mod_hierarchy_truthy(self,
                                                                            _zigzag_runner_factory,
                                                                            computed_hierarchy_config_file_truthy):
        """ Verify that value can be computed based on a true boolean condition
        """

        zz_runner = _zigzag_runner_factory('junit.xml', computed_hierarchy_config_file_truthy, {})
        zz_runner.add_test_case('passed')
        zz_runner.assert_invoke_zigzag()
        test = zz_runner.tests[0]
        qtest_parent_test_cycle_name = test.qtest_parent_test_cycles[0].name

        # Expectations
        parent_test_cycle_name_exp = 'foo'

        # Test
        assert parent_test_cycle_name_exp == qtest_parent_test_cycle_name

    # noinspection PyUnresolvedReferences
    def test_publish_single_passing_test_with_computed_mod_hierarchy_falsey(self,
                                                                            _zigzag_runner_factory,
                                                                            computed_hierarchy_config_file_falsey):
        """ Verify that value can be computed based on a false boolean condition
        """

        zz_runner = _zigzag_runner_factory('junit.xml', computed_hierarchy_config_file_falsey, {})
        zz_runner.add_test_case('passed')
        zz_runner.assert_invoke_zigzag()
        test = zz_runner.tests[0]
        qtest_parent_test_cycle_name = test.qtest_parent_test_cycles[0].name

        # Expectations
        parent_test_cycle_name_exp = 'bar'

        # Test
        assert parent_test_cycle_name_exp == qtest_parent_test_cycle_name


class TestConfigNegative(object):

    def test_bad_module_hierarchy(self, _zigzag_runner_factory, bad_hierarchy_config_file):
        """Verify that an error will be raised when the wrong data type is provided for module_hierarchy;
           specifically a comma delimited string instead of an array.
        """

        zz_runner = _zigzag_runner_factory('junit.xml', bad_hierarchy_config_file, {})
        zz_runner.add_test_case('passed')
        expected_message = "does not comply with schema: u'node1, node2' is not of type u'array'"

        with pytest.raises(ZigZagConfigError, match=expected_message):
            zz_runner.assert_invoke_zigzag()

    def test_missing_test_cycle(self, _zigzag_runner_factory, no_test_cycle_config, asc_global_props):
        """Verify that an error will be raised when the test_cycle config is not present"""

        zz_runner = _zigzag_runner_factory('junit.xml', no_test_cycle_config, asc_global_props)
        zz_runner.add_test_case('passed')
        expected_message = "'test_cycle' is a required property"

        with pytest.raises(ZigZagConfigError, match=expected_message):
            zz_runner.assert_invoke_zigzag()

    def test_missing_project_id(self, _zigzag_runner_factory, no_project_id_config, asc_global_props):
        """Verify that an error will be raised when the project_id config is not present"""

        zz_runner = _zigzag_runner_factory('junit.xml', no_project_id_config, asc_global_props)
        zz_runner.add_test_case('passed')
        expected_message = "'project_id' is a required property"

        with pytest.raises(ZigZagConfigError, match=expected_message):
            zz_runner.assert_invoke_zigzag()

    def test_missing_module_module_hierarchy(self,
                                             _zigzag_runner_factory,
                                             no_module_hierarchy_config,
                                             asc_global_props):
        """Verify that an error will be raised when the module_hierarchy config is not present"""

        zz_runner = _zigzag_runner_factory('junit.xml', no_module_hierarchy_config, asc_global_props)
        zz_runner.add_test_case('passed')
        expected_message = "'module_hierarchy' is a required property"

        with pytest.raises(ZigZagConfigError, match=expected_message):
            zz_runner.assert_invoke_zigzag()

    def test_required_property_evaluates_to_empty_string(self,
                                                         tmpdir_factory,
                                                         qtest_env_vars,
                                                         _configure_test_environment,
                                                         required_configs):
        """This tests the scenario when a config is present in the config file but its value is not present

        Example:
            "test_cycle": "{{ I_AM_NOT_A_REAL_PROPERTY }}"
        """
        temp_dir = tmpdir_factory.mktemp('data')
        props = {}
        root_test_cycle, root_req_module = _configure_test_environment
        junit_xml_file_path = temp_dir.join('junit.xml').strpath

        zz_runner = ZigZagRunner(qtest_env_vars['QTEST_API_TOKEN'],
                                 qtest_env_vars['QTEST_SANDBOX_PROJECT_ID'],
                                 root_test_cycle,
                                 root_req_module,
                                 junit_xml_file_path,
                                 required_configs,
                                 props)

        zz_runner.add_test_case('passed')

        expected_message = "The config 'project_id' was not found in the config file"

        with pytest.raises(ZigZagConfigError, match=expected_message):
            zz_runner.assert_invoke_zigzag()
