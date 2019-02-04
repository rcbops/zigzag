# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import collections
from zigzag.zigzag_error import ZigZagConfigError
from json import loads
from jinja2 import Template


class ZigZagConfig(collections.MutableMapping):
    """An ABC of a MutableMapping (behaves like dict)
    Will raise custom errors attempting to access keys that dont exist
    """

    def __init__(self, config_file_path, global_props):
        """Create a new ZigZagConfig

        Args:
            config_file_path (str): the path to the config file
            global_props (dict): the props from the XML
        """
        try:
            conf_template = open(config_file_path, 'r')
            template = Template(conf_template.read())
            rendered_zigzag_config_str = template.render(global_props)

            # remove empty strings
            self._config = {k: v for k, v in list(loads(rendered_zigzag_config_str).items()) if v != ''}

        except (OSError, IOError):
            raise ZigZagConfigError("Failed to load '{}' config file!".format(config_file_path))
        except ValueError as e:
            raise ZigZagConfigError("The '{}' config file is not valid JSON: {}".format(config_file_path, str(e)))

    def __getitem__(self, key):
        try:
            return self._config[key]
        except KeyError:
            raise ZigZagConfigError("The config '{}' was not found in the config file".format(key))

    def __setitem__(self, key, value):
        self._config[key] = value

    def __delitem__(self, key):
        try:
            del self._config[key]
        except KeyError:
            raise ZigZagConfigError("The config '{}' was not found in the config file".format(key))

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)
