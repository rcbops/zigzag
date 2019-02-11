# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
from zigzag.zigzag_error import ZigZagConfigError
from pkg_resources import resource_stream
from jsonschema import validate, ValidationError
from json import loads
from jinja2 import Template
import time
import copy


class ZigZagConfig(object):
    """A config object for zigzag
    Will raise custom errors attempting to access keys that dont exist
    """

    def __init__(self, config_file_path, global_props):
        """Create a new ZigZagConfig

        Args:
            config_file_path (str): the path to the config file
            global_props (dict): the props from the XML
        """
        try:
            with open(config_file_path, 'r') as f:
                self._config_dict = loads(f.read())
            self._global_props = global_props
            schema = loads(resource_stream('zigzag',
                                           'data/schema/zigzag-config.schema.json').read().decode())
            validate(self._config_dict, schema)

        except (OSError, IOError):
            raise ZigZagConfigError("Failed to load '{}' config file!".format(config_file_path))
        except ValueError as e:
            raise ZigZagConfigError("The '{}' config file is not valid JSON: {}".format(config_file_path, str(e)))
        except ValidationError as e:
            raise ZigZagConfigError("Config file '{}' does not comply with schema: {}".format(config_file_path, str(e)))

    def get_config(self, config_name, test_log=None):
        """Gets a config can be evaluated with optional test_log

        Args:
            config_name (str): the name of the config to get
            test_log (ZigZagTestLog): an optional test log to evaluate special test specific variables

        Returns:
            str : any type that can be represented in JSON
            dict
            list
            None
        """

        try:
            if test_log:
                # add testcase specific info to the props
                props = copy.copy(self._global_props)
                props['zz_testcase_class'] = test_log.classname
            else:
                props = self._global_props

            props['strftime'] = time.strftime
            pre_render_config_value = self._config_dict['zigzag'][config_name]
            value_type = type(pre_render_config_value)
            if any([value_type is str, value_type is unicode]):
                value = Template(self._config_dict['zigzag'][config_name]).render(props)
            elif value_type is list:
                # try to render each object
                value = [Template(v).render(props) for v in pre_render_config_value]
            elif any([value_type is None, value_type is int, value_type is float]):
                value = pre_render_config_value

        except KeyError:
            raise ZigZagConfigError("The config '{}' was not found in the config file".format(config_name))

        if value == '':  # TODO decide what should be an allowable value None??? emptystring????
            raise ZigZagConfigError("The config '{}' was not found in the config file".format(config_name))

        return value
