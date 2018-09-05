# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import re
import json
import pytest
import requests


# ======================================================================================================================
# Helpers
# ======================================================================================================================
# noinspection PyUnresolvedReferences
@pytest.helpers.register
def search_qtest(qtest_api_token, qtest_project_id, object_type, query, fields=None):
    """Search qTest for objects matching a given query. (This helper exists because the swagger_client search API
    returns a really useless model)

    Args:
        qtest_api_token (str): The API token for the target qTest project.
        qtest_project_id (int): The target qTest project to use for publishing results.
        object_type (str): The type of qTest objects to search.
            (Valid values: 'requirements', 'test-cases', 'test-runs', 'defects')
        query (str): The query to execute against the given object type.
        fields ([str]): A list of qTest object field names to capture in the return data.
            (All fields captured if None is specified)

    Returns:
        dict: A dictionary representing the JSON return data from the endpoint.

    Raises:
        RuntimeError: qTest API request failed.
    """

    fields = fields if fields else ['*']
    headers = {'Authorization': qtest_api_token, 'Content-Type': 'application/json'}
    endpoint = \
        "https://apitryout.qtestnet.com/api/v3/projects/{}/search?pageSize=100&page=1".format(str(qtest_project_id))

    body = {'object_type': object_type,
            'fields': fields,
            'query': "{}".format(query)}

    try:
        r = requests.post(endpoint, data=json.dumps(body), headers=headers)
        r.raise_for_status()
        parsed = json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise RuntimeError("The qTest API reported an error!\n"
                           "Status code: {}\n"
                           "Reason: {}\n".format(e.response.status_code, e.response.reason))

    return parsed


# noinspection PyUnresolvedReferences
@pytest.helpers.register
def get_qtest_property(model, prop_name):
    """Get the value for a qTest swagger_client model property. This helper will intelligently search both standard
    qTest swagger_client model attributes as well as custom fields set by the qTest admin of the qTest project under
    test.

    Enabling 'promiscuous' mode (default) will attempt to retrieve the property value against either the 'field_value'
    or 'field_value_name' attributes of the model. If 'promiscuous' mode is disabled then retrieval of the expected
    property value will only be made against the 'field_value' attribute of the model.

    Args:
        model (object): Any model from the 'swagger_client.models' namespace.
        prop_name (str): Target property name to use for value validation.

    Returns:
        [obj]: list of values for desired property. Data type could be anything depending on what the model specifies.
            Also, multiple values will be returned if the requested property is a custom qTest field.

    Raises:
        AssertionError: Property name does not exist.
    """

    actual_values = []
    model_dict = model.to_dict()
    try:
        custom_props = {p['field_name']: (p['field_value'], p['field_value_name']) for p in model_dict['properties']}
    except KeyError:
        custom_props = {}

    if prop_name in model_dict:
        actual_values.append(model_dict[prop_name])
    elif prop_name in custom_props:
        actual_values = custom_props[prop_name]
    else:
        raise AssertionError("The '{}' property not found in the provided swagger_client model!".format(prop_name))

    return actual_values


# noinspection PyUnresolvedReferences
@pytest.helpers.register
def assert_qtest_property(model, prop_name, exp_prop_value, promiscuous=True):
    """Assert that a qTest swagger_client model has a property that matches the expected value. This assert will
    intelligently search both standard qTest swagger_client model attributes as well as custom fields set by the
    qTest admin of the qTest project under test.

    Enabling 'promiscuous' mode (default) will attempt to match the property value against either the 'field_value' or
    'field_value_name' attributes of the model. If 'promiscuous' mode is disabled then validation of the expected
    property value will only be made against the 'field_value' attribute of the model.

    Args:
        model (object): Any model from the 'swagger_client.models' namespace.
        prop_name (str): Target property name to use for value validation.
        exp_prop_value (str): Expected value for the given property name.
        promiscuous (bool): Flag for indicating whether to run assertion in 'promiscuous' mode or not. (See above)

    Raises:
        AssertionError: Property name does not exist or property value does not match expected value.
    """

    actual_values = get_qtest_property(model, prop_name)

    if promiscuous:
        assert exp_prop_value in actual_values
    else:
        assert actual_values[0] == exp_prop_value


# noinspection PyUnresolvedReferences
@pytest.helpers.register
def assert_qtest_property_match(model, prop_name, exp_prop_regex, regex_flags=0, promiscuous=True):
    """Assert that a qTest swagger_client model has a property that matches a given regular expression. This assert will
    intelligently search both standard qTest swagger_client model attributes as well as custom fields set by the
    qTest admin of the qTest project under test.

    NOTE: Regex is run in 'match' mode with this helper!

    Enabling 'promiscuous' mode (default) will attempt to match the property value against either the 'field_value' or
    'field_value_name' attributes of the model. If 'promiscuous' mode is disabled then validation of the expected
    property value will only be made against the 'field_value' attribute of the model.

    Args:
        model (object): Any model from the 'swagger_client.models' namespace.
        prop_name (str): Target property name to use for value validation.
        exp_prop_regex (str): Regular expression pattern that property value is expected to match.
        regex_flags (int): Flags to pass to the regex evaluator to alter pattern matching behavior.
        promiscuous (bool): Flag for indicating whether to run assertion in 'promiscuous' mode or not. (See above)

    Raises:
        AssertionError: Property name does not exist or property value failed regular expression match.
    """

    actual_values = get_qtest_property(model, prop_name)

    if promiscuous:
        assert any([re.match(exp_prop_regex, value, regex_flags) for value in actual_values if type(value) is str])
    else:
        assert re.match(exp_prop_regex, actual_values[0], regex_flags)


# noinspection PyUnresolvedReferences
@pytest.helpers.register
def assert_qtest_property_search(model, prop_name, exp_prop_regex, regex_flags=0, promiscuous=True):
    """Assert that a qTest swagger_client model has a property that matches a given regular expression. This assert will
    intelligently search both standard qTest swagger_client model attributes as well as custom fields set by the
    qTest admin of the qTest project under test.

    NOTE: Regex is run in 'search' mode with this helper!

    Enabling 'promiscuous' mode (default) will attempt to match the property value against either the 'field_value' or
    'field_value_name' attributes of the model. If 'promiscuous' mode is disabled then validation of the expected
    property value will only be made against the 'field_value' attribute of the model.

    Args:
        model (object): Any model from the 'swagger_client.models' namespace.
        prop_name (str): Target property name to use for value validation.
        exp_prop_regex (str): Regular expression pattern that property value is expected to match.
        regex_flags (int): Flags to pass to the regex evaluator to alter pattern matching behavior.
        promiscuous (bool): Flag for indicating whether to run assertion in 'promiscuous' mode or not. (See above)

    Raises:
        AssertionError: Property name does not exist or property value failed regular expression match.
    """

    actual_values = get_qtest_property(model, prop_name)

    if promiscuous:
        assert any([re.search(exp_prop_regex, value, regex_flags) for value in actual_values if type(value) is str])
    else:
        assert re.search(exp_prop_regex, actual_values[0], regex_flags)
