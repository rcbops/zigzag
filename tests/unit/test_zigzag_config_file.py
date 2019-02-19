# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
from zigzag.zigzag_config import ZigZagConfig
from zigzag.zigzag_error import ZigZagConfigError

# ======================================================================================================================
# Fixtures
# ======================================================================================================================


@pytest.fixture(scope='session')
def config_with_interpolation(tmpdir_factory):
    """config with one value in a jinga template"""
    config = \
        """
        {
            "zigzag": {
                "test_cycle": "pike",
                "project_id": "12345",
                "module_hierarchy": ["one","two","three"],
                "path_to_test_exec_dir": "{{ FOO }}"
            }
        }
        """  # noqa

    config_path = tmpdir_factory.mktemp('data').join('./conf.json').strpath

    with open(str(config_path), 'w') as f:
        f.write(config)

    return config_path


@pytest.fixture(scope='session')
def config_with_zz_variable(tmpdir_factory):
    """config with one value in a jinga template uses zz variable"""
    config = \
        """
        {
            "zigzag": {
                "test_cycle": "pike",
                "project_id": "12345",
                "module_hierarchy": ["one", "two", "{{ zz_testcase_class }}"],
                "path_to_test_exec_dir": "foo/bar/tests"
            }
        }
        """  # noqa

    config_path = tmpdir_factory.mktemp('data').join('./conf.json').strpath

    with open(str(config_path), 'w') as f:
        f.write(config)

    return config_path


@pytest.fixture(scope='session')
def config_missing_zigzag_key(tmpdir_factory):
    """config missing zigzag key"""
    config = \
        """
        {
            "test_cycle": "pike",
            "project_id": "12345",
            "module_hierarchy": ["one","two","three"],
            "path_to_test_exec_dir": "{{ FOO }}"
        }
        """  # noqa

    config_path = tmpdir_factory.mktemp('data').join('./conf.json').strpath

    with open(str(config_path), 'w') as f:
        f.write(config)

    return config_path


@pytest.fixture(scope='session')
def config_missing_project_id_key(tmpdir_factory):
    """config missing project_id key"""
    config = \
        """
        {
            "zigzag": {
                "test_cycle": "pike",
                "module_hierarchy": ["one","two","three"],
                "path_to_test_exec_dir": "{{ FOO }}"
            }
        }
        """  # noqa

    config_path = tmpdir_factory.mktemp('data').join('./conf.json').strpath

    with open(str(config_path), 'w') as f:
        f.write(config)

    return config_path


@pytest.fixture(scope='session')
def module_hierarchy_two_nodes(tmpdir_factory):
    """config with module_hierarchy containing two items"""
    config = \
        """
        {
            "zigzag": {
                "project_id": "12345",
                "test_cycle": "pike",
                "module_hierarchy": ["{{ NODE_ONE }}", "{{ NODE_TWO }}"],
                "path_to_test_exec_dir": "{{ FOO }}"
            }
        }
        """  # noqa

    config_path = tmpdir_factory.mktemp('data').join('./conf.json').strpath

    with open(str(config_path), 'w') as f:
        f.write(config)

    return config_path


@pytest.fixture(scope='session')
def empty_module_hierarchy(tmpdir_factory):
    """Config file with an empty module_hierarchy"""
    config = \
        """
        {
            "zigzag": {
                "project_id": "12345",
                "test_cycle": "pike",
                "module_hierarchy": [],
                "path_to_test_exec_dir": "{{ FOO }}"
            }
        }
        """  # noqa

    config_path = tmpdir_factory.mktemp('data').join('./conf.json').strpath

    with open(str(config_path), 'w') as f:
        f.write(config)

    return config_path


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestZigZagConfig(object):
    """Test cases for ZigZagConfig"""

    def test_pull_value_from_properties(self, config_with_interpolation):
        """Test that we can interpolate one value successfully"""

        properties = {'FOO': '/Hello/is/it/me/youre/looking/for'}
        config = ZigZagConfig(config_with_interpolation, properties)
        assert properties['FOO'] == config.get_config('path_to_test_exec_dir')

    def test_access_config_not_present(self, config_with_interpolation):
        """Test that we will raise error if value defined in config
        is not present in the global properties"""

        properties = {}
        config = ZigZagConfig(config_with_interpolation, properties)
        expected_message = "The config setting 'path_to_test_exec_dir' was not found in the config file"

        with pytest.raises(ZigZagConfigError, match=expected_message):
            config.get_config('path_to_test_exec_dir')

    def test_config_not_json(self, invalid_zigzag_config_file):
        """Test that we will raise error if value defined in config
        is not present in the global properties"""

        properties = {}
        expected_message = 'config file is not valid JSON'
        with pytest.raises(ZigZagConfigError, match=expected_message):
            ZigZagConfig(invalid_zigzag_config_file, properties)

    def test_zz_testcase_class_variable(self, config_with_zz_variable, mocker):
        """Test that we can use the 'zz_testcase_class' special variable
        in a ZigZag config"""

        # Mock
        zz_test_log = mocker.MagicMock()
        zz_test_log.classname = 'this.is.the.classname'

        properties = {}
        config = ZigZagConfig(config_with_zz_variable, properties)
        assert ['one', 'two', zz_test_log.classname] == config.get_config('module_hierarchy', zz_test_log)

    def test_missing_zigzag_key(self, config_missing_zigzag_key):
        """Provide json that should not pass the validation"""
        properties = {}
        expected_message = "'zigzag' is a required property"

        with pytest.raises(ZigZagConfigError, match=expected_message):
            ZigZagConfig(config_missing_zigzag_key, properties)

    def test_missing_required_config(self, config_missing_project_id_key):
        """Provide json that should not pass the validation"""
        properties = {}
        expected_message = "'project_id' is a required property"

        with pytest.raises(ZigZagConfigError, match=expected_message):
            ZigZagConfig(config_missing_project_id_key, properties)

    def test_list_value_containing_empty_value(self, module_hierarchy_two_nodes):
        """Test a config where a list contains an empty string"""

        properties = {'NODE_ONE': 'FOO'}  # do not supply NODE_TWO
        config = ZigZagConfig(module_hierarchy_two_nodes, properties)
        expected_message = 'The config module_hierarchy contained an empty value'

        with pytest.raises(ZigZagConfigError, match=expected_message):
            config.get_config('module_hierarchy')

    def test_empty_list(self, empty_module_hierarchy):
        """Test a config where the value is an empty list"""

        config = ZigZagConfig(empty_module_hierarchy, {})
        expected_message = "The config setting 'module_hierarchy' was not found in the config file"

        with pytest.raises(ZigZagConfigError, match=expected_message):
            config.get_config('module_hierarchy')
