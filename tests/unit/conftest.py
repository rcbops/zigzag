# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
pytest_plugins = ['helpers_namespace']


# ======================================================================================================================
# Helpers
# ======================================================================================================================
# noinspection PyUnresolvedReferences
@pytest.helpers.register
def merge_dicts(*args):
    """Given any number of dicts, shallow copy and merge into a new dict, precedence goes to key value pairs in latter
    dicts.

    Args:
        *args (list(dict)): A list of dictionaries to be merged.

    Returns:
        dict: A merged dictionary.
    """

    result = {}
    for dictionary in args:
        result.update(dictionary)
    return result


# noinspection PyUnresolvedReferences
@pytest.helpers.register
def is_sub_dict(small, big):
    """Determine if one dictionary is a subset of another dictionary.

    Args:
        small (dict): A dictionary that is proposed to be a subset of another dictionary.
        big (dict): A dictionary that is a superset of another dictionary.

    Returns:
        bool: A bool indicating if the small dictionary is in fact a sub-dictionary of big
    """

    return dict(big, **small) == big


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
@pytest.fixture(scope='session')
def default_global_properties():
    """Default global properties which can be used to construct valid JUnitXML documents."""

    return \
        """
                <properties>
                    <property name="BUILD_URL" value="https://rpc.jenkins.cit.rackspace.net/job/PM_rpc-openstack-pike-rc-xenial_mnaio_no_artifacts-swift-system/78/"/>
                    <property name="BUILD_NUMBER" value="78"/>
                    <property name="RE_JOB_ACTION" value="system"/>
                    <property name="RE_JOB_IMAGE" value="xenial_mnaio_no_artifacts"/>
                    <property name="RE_JOB_SCENARIO" value="swift"/>
                    <property name="RE_JOB_BRANCH" value="pike-rc"/>
                    <property name="RPC_RELEASE" value="r16.2.0"/>
                    <property name="RPC_PRODUCT_RELEASE" value="pike"/>
                    <property name="OS_ARTIFACT_SHA" value="Unknown"/>
                    <property name="PYTHON_ARTIFACT_SHA" value="Unknown"/>
                    <property name="APT_ARTIFACT_SHA" value="Unknown"/>
                    <property name="REPO_URL" value="https://github.com/rcbops/rpc-openstack"/>
                    <property name="JOB_NAME" value="PM_rpc-openstack-pike-rc-xenial_mnaio_no_artifacts-swift-system"/>
                    <property name="MOLECULE_TEST_REPO" value="molecule-validate-neutron-deploy"/>
                    <property name="MOLECULE_SCENARIO_NAME" value="default"/>
                    <property name="ci-environment" value="asc"/>
                </properties>
        """  # noqa


@pytest.fixture(scope='session')
def default_testcase_properties():
    """Default test case properties which can be used to construct valid JUnitXML documents."""

    return \
        """
                    <properties>
                        <property name="jira" value="ASC-123"/>
                        <property name="jira" value="ASC-456"/>
                        <property name="test_id" value="1"/>
                        <property name="test_step" value="false"/>
                        <property name="start_time" value="2018-04-10T21:38:18Z"/>
                        <property name="end_time" value="2018-04-10T21:38:19Z"/>
                    </properties>
        """


@pytest.fixture(scope='session')
def default_testcase_elements():
    """Default test case properties which can be used to construct valid JUnitXML documents."""

    return \
        """
                    <system-out>stdout</system-out>
                    <system-err>stderr</system-err>
        """


@pytest.fixture(scope='session')
def invalid_json_config(tmpdir_factory,
                        default_global_properties,
                        default_testcase_properties,
                        default_testcase_elements):
    """config sample"""
    config = \
"""
{
    "test_cycle": "pike",
    "project_id": 12345,
    "module_hierarchy": ["one","two","three"],
    "path_to_test_exec_dir
}
""" # noqa

    config_path = tmpdir_factory.mktemp('data').join('./conf.json').strpath

    with open(str(config_path), 'w') as f:
        f.write(config)

    return config_path


@pytest.fixture(scope='session')
def simple_json_config(tmpdir_factory):
    """config sample"""
    config = \
"""
{
    "zigzag": {
        "test_cycle": "pike",
        "project_id": "12345",
        "build_url": "https://bar.com/foo",
        "build_number": "78",
        "module_hierarchy": ["one","two","three"],
        "path_to_test_exec_dir": "{{ '' }}"
    }
}
""" # noqa

    config_path = tmpdir_factory.mktemp('data').join('./conf.json').strpath

    with open(str(config_path), 'w') as f:
        f.write(config)

    return config_path


@pytest.fixture(scope='session')
def single_passing_xml(tmpdir_factory,
                       default_global_properties,
                       default_testcase_properties,
                       default_testcase_elements):
    """JUnitXML sample representing a single passing test."""

    filename = tmpdir_factory.mktemp('data').join('single_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def invalid_zigzag_config_file(tmpdir_factory,
                               default_global_properties,
                               default_testcase_properties,
                               default_testcase_elements):
    """JUnitXML sample representing a single passing test."""

    filename = tmpdir_factory.mktemp('data').join('config_file.xml').strpath
    config_json = \
        """{
             "environment_variables": {
               "BUILD_URL": "url",
           """

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def asc_zigzag_config_file(tmpdir_factory):
    """A config for zigzag used by the ASC team"""

    filename = tmpdir_factory.mktemp('data').join('config_file.json').strpath
    config_json = \
        """{
              "pytest_zigzag_env_vars": {
                "BUILD_URL": null,
                "BUILD_NUMBER": null,
                "RE_JOB_ACTION": null,
                "RE_JOB_IMAGE": null,
                "RE_JOB_SCENARIO": null,
                "RE_JOB_BRANCH": null,
                "RPC_RELEASE": null,
                "RPC_PRODUCT_RELEASE": null,
                "OS_ARTIFACT_SHA": null,
                "PYTHON_ARTIFACT_SHA": null,
                "APT_ARTIFACT_SHA": null,
                "REPO_URL": null,
                "GIT_URL": null,
                "JOB_NAME": null,
                "MOLECULE_TEST_REPO": null,
                "MOLECULE_SCENARIO_NAME": null,
                "PATH_TO_TEST_EXEC_DIR": null,
                "MOLECULE_GIT_COMMIT": null,
                "GIT_COMMIT": null
              },
              "zigzag": {
                "test_cycle": "{{ RPC_PRODUCT_RELEASE }}",
                "project_id": "12345",
                "module_hierarchy": [
                  "{{RPC_RELEASE}}",
                  "{{JOB_NAME}}",
                  "{{MOLECULE_TEST_REPO}}",
                  "{{zz_testcase_class}}"
                ],
                "path_to_test_exec_dir": "/molecule/default/tests",
                "build_url": "{{ BUILD_URL }}",
                "build_number": "{{ BUILD_NUMBER }}",
                "project_repo_name": "rpc-openstack",
                "project_branch": "{{ RE_JOB_BRANCH }}",
                "project_fork": "rcbops",
                "project_commit": null,
                "test_repo_name": "{{ MOLECULE_TEST_REPO }}",
                "test_branch": "{{ RE_JOB_BRANCH }}",
                "test_fork": "rcbops",
                "test_commit": "{{ MOLECULE_GIT_COMMIT }}"
              }
            }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def mk8s_zigzag_config_file(tmpdir_factory):
    """A config for zigzag used by the ASC team"""

    filename = tmpdir_factory.mktemp('data').join('config_file.json').strpath
    config_json = \
        """{
              "pytest_zigzag_env_vars": {
                "BUILD_URL": null,
                "BUILD_NUMBER": null,
                "BUILD_ID": null,
                "JOB_NAME": null,
                "BUILD_TAG": null,
                "JENKINS_URL": null,
                "EXECUTOR_NUMBER": null,
                "WORKSPACE": null,
                "CVS_BRANCH": null,
                "GIT_COMMIT": null,
                "GIT_URL": null,
                "GIT_BRANCH": null,
                "GIT_LOCAL_BRANCH": null,
                "GIT_AUTHOR_NAME": null,
                "GIT_AUTHOR_EMAIL": null,
                "BRANCH_NAME": null,
                "CHANGE_AUTHOR_DISPLAY_NAME": null,
                "CHANGE_AUTHOR": null,
                "CHANGE_BRANCH": null,
                "CHANGE_FORK": null,
                "CHANGE_ID": null,
                "CHANGE_TARGET": null,
                "CHANGE_TITLE": null,
                "CHANGE_URL": null,
                "JOB_URL": null,
                "NODE_LABELS": null,
                "NODE_NAME": null,
                "PWD": null,
                "STAGE_NAME": null
              },
              "zigzag": {
                "test_cycle": "{{ 'PR' if CHANGE_BRANCH else BRANCH_NAME }}",
                "project_id": "12345",
                "module_hierarchy": [
                  "{{ zz_testcase_class }}"
                ],
                "path_to_test_exec_dir": "tools/installer/tests",
                "build_url": "{{ BUILD_URL }}",
                "build_number": "{{ BUILD_NUMBER }}",
                "project_repo_name": "mk8s",
                "project_branch": "{{ CHANGE_BRANCH }}",
                "project_fork": "{{ CHANGE_FORK if CHANGE_FORK else 'rcbops' }}",
                "project_commit": "{{ GIT_COMMIT }}",
                "test_repo_name": "mk8s",
                "test_branch": "{{ CHANGE_BRANCH }}",
                "test_fork": "{{ CHANGE_FORK if CHANGE_FORK else 'rcbops' }}",
                "test_commit": "{{ GIT_COMMIT }}"
              }
            }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def valid_zigzag_config_file(tmpdir_factory,
                             default_global_properties,
                             default_testcase_properties,
                             default_testcase_elements):
    """JUnitXML sample representing a single passing test."""

    filename = tmpdir_factory.mktemp('data').join('config_file.xml').strpath
    config_json = \
        """{
             "pytest_zigzag_env_vars": {
               "BUILD_URL": "url",
               "BUILD_NUMBER": null,
               "RE_JOB_ACTION": null,
               "RE_JOB_IMAGE": null,
               "RE_JOB_SCENARIO": null,
               "RE_JOB_BRANCH": null,
               "RPC_RELEASE": null,
               "RPC_PRODUCT_RELEASE": null,
               "OS_ARTIFACT_SHA": null,
               "PYTHON_ARTIFACT_SHA": null,
               "APT_ARTIFACT_SHA": null,
               "REPO_URL": "https://github.com/rcbops/zigzag_asc",
               "GIT_URL": "https://github.com/rcbops/zigzag_mk8s",
               "JOB_NAME": null,
               "MOLECULE_TEST_REPO": "pytest-zigzag",
               "MOLECULE_SCENARIO_NAME": "molecule_scenario",
               "PATH_TO_TEST_EXEC_DIR": "custom_test_dir/",
               "MOLECULE_GIT_COMMIT": "8216c9449ef99216c922f2f2fd01f28e412cfe87",
               "GIT_COMMIT": "mk8s_gitsha"
             }
           }"""

    with open(filename, 'w') as f:
        f.write(config_json)

    return filename


@pytest.fixture(scope='session')
def single_fail_xml(tmpdir_factory,
                    default_global_properties,
                    default_testcase_properties,
                    default_testcase_elements):
    """JUnitXML sample representing a single failing test."""

    filename = tmpdir_factory.mktemp('data').join('single_fail.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def single_error_xml(tmpdir_factory,
                     default_global_properties,
                     default_testcase_properties,
                     default_testcase_elements):
    """JUnitXML sample representing a single erroring test."""

    filename = tmpdir_factory.mktemp('data').join('single_error.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="20"
            name="test_error[ansible://localhost]" time="0.00208067893982">
                {testcase_properties}

                <error message="test setup failure">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            @pytest.fixture
            def error_fixture(host):
        &gt;       raise RuntimeError(&apos;oops&apos;)
        E       RuntimeError: oops

        tests/test_default.py:10: RuntimeError</error>
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def single_skip_xml(tmpdir_factory,
                    default_global_properties,
                    default_testcase_properties,
                    default_testcase_elements):
    """JUnitXML sample representing a single skipping test."""

    filename = tmpdir_factory.mktemp('data').join('single_skip.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="24"
            name="test_skip[ansible://localhost]" time="0.00197100639343">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def flat_all_passing_xml(tmpdir_factory,
                         default_global_properties,
                         default_testcase_properties,
                         default_testcase_elements):
    """JUnitXML sample representing multiple passing test cases."""

    filename = tmpdir_factory.mktemp('data').join('flat_all_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass1[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="12"
            name="test_pass2[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="15"
            name="test_pass3[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="18"
            name="test_pass4[ansible://localhost]" time="0.00314617156982">
                {testcase_properties}
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="21"
            name="test_pass5[ansible://localhost]" time="0.00332307815552">
                {testcase_properties}
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def suite_all_passing_xml(tmpdir_factory,
                          default_global_properties,
                          default_testcase_properties,
                          default_testcase_elements):
    """JUnitXML sample representing multiple passing test cases in a test suite. (Tests within a Python class)"""

    filename = tmpdir_factory.mktemp('data').join('suite_all_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
            <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default.TestSuite" file="tests/test_default.py" line="8"
            name="test_pass1[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestSuite" file="tests/test_default.py" line="12"
            name="test_pass2[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestSuite" file="tests/test_default.py" line="15"
            name="test_pass3[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestSuite" file="tests/test_default.py" line="18"
            name="test_pass4[ansible://localhost]" time="0.00314617156982">
                {testcase_properties}
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default.TestSuite" file="tests/test_default.py" line="21"
            name="test_pass5[ansible://localhost]" time="0.00332307815552">
                {testcase_properties}
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def flat_mix_status_xml(tmpdir_factory,
                        default_global_properties,
                        default_testcase_properties,
                        default_testcase_elements):
    """JUnitXML sample representing mixed status for multiple test cases."""

    filename = tmpdir_factory.mktemp('data').join('flat_mix_status.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="1" failures="1" name="pytest" skips="1" tests="4" time="1.901">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="12"
            name="test_pass[ansible://localhost]" time="0.0034921169281">
                {testcase_properties}
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="20"
            name="test_error[ansible://localhost]" time="0.00208067893982">
                {testcase_properties}
                <error message="test setup failure">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            @pytest.fixture
            def error_fixture(host):
        &gt;       raise RuntimeError(&apos;oops&apos;)
        E       RuntimeError: oops

        tests/test_default.py:10: RuntimeError</error>
                {testcase_elements}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="24"
            name="test_skip[ansible://localhost]" time="0.00197100639343">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def bad_xml(tmpdir_factory):
    """JUnitXML sample representing invalid XML."""

    filename = tmpdir_factory.mktemp('data').join('bad.xml').strpath
    junit_xml = "Totally Bogus Content"

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def bad_junit_root(tmpdir_factory):
    """JUnitXML sample representing XML that is missing all relevant content."""

    filename = tmpdir_factory.mktemp('data').join('bad_junit_root.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <bad>
        </bad>
        """

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def missing_testcase_properties_xml(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing a test case that is missing the test case "properties" element."""

    filename = tmpdir_factory.mktemp('data').join('missing_testcase_properties.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass[ansible://localhost]" time="0.00372695922852"/>
        </testsuite>
        """.format(global_properties=default_global_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def missing_test_id_xml(tmpdir_factory, default_global_properties, default_testcase_elements):
    """JUnitXML sample representing a test case that has a missing test id property element."""

    filename = tmpdir_factory.mktemp('data').join('missing_test_id.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass[ansible://localhost]" time="0.00372695922852"/>
                <properties>
                    <property name="start_time" value="2018-04-10T21:38:18Z"/>
                    <property name="start_time" value="2018-04-10T21:38:18Z"/>
                    <property name="end_time" value="2018-04-10T21:38:19Z"/>
                </properties>
                {testcase_elements}
        </testsuite>
        """.format(global_properties=default_global_properties, testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def xml_with_unknown_elements(tmpdir_factory, default_global_properties):
    """JUnitXML sample representing an xml document missing testcases."""

    filename = tmpdir_factory.mktemp('data').join('missing_test_id.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuitefoo errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
        </testsuitefoo>
        """.format(global_properties=default_global_properties)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def missing_build_url_xml(tmpdir_factory, default_testcase_properties, default_testcase_elements):
    """JUnitXML sample representing a test suite that is missing the "BUILD_URL" property."""

    filename = tmpdir_factory.mktemp('data').join('missing_build_url.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            <properties>
                <property name="BUILD_NUMBER" value="Unknown"/>
                <property name="BUILD_NUMBER" value="Unknown"/>
                <property name="RE_JOB_ACTION" value="Unknown"/>
                <property name="RE_JOB_IMAGE" value="Unknown"/>
                <property name="RE_JOB_SCENARIO" value="Unknown"/>
                <property name="RE_JOB_BRANCH" value="Unknown"/>
                <property name="RPC_RELEASE" value="Unknown"/>
                <property name="RPC_PRODUCT_RELEASE" value="Unknown"/>
                <property name="OS_ARTIFACT_SHA" value="Unknown"/>
                <property name="PYTHON_ARTIFACT_SHA" value="Unknown"/>
                <property name="APT_ARTIFACT_SHA" value="Unknown"/>
                <property name="REPO_URL" value="Unknown"/>
            </properties>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass[ansible://localhost]" time="0.00372695922852"/>
                {testcase_properties}
                {testcase_elements}
        </testsuite>
        """.format(testcase_properties=default_testcase_properties, testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def classname_with_dashes_xml(tmpdir_factory,
                              default_global_properties,
                              default_testcase_properties,
                              default_testcase_elements):
    """JUnitXML sample representing a testcase that has a 'classname' attribute which contains dashes for the py.test
    filename."""

    filename = tmpdir_factory.mktemp('data').join('classname_with_dashes.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="test.tests.test_for_acs-150.TestForRPC10PlusPostDeploymentQCProcess"
            file="tests/test_for_acs-150.py" line="140"
            name="test_verify_kibana_horizon_access_with_no_ssh[_testinfra_host0]" time="0.00372695922852">
                {testcase_properties}
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def invalid_classname_xml(tmpdir_factory,
                          default_global_properties,
                          default_testcase_properties,
                          default_testcase_elements):
    """JUnitXML sample representing a testcase that has an invalid 'classname' attribute which is used to build the
    results hierarchy in the '_generate_module_hierarchy' function."""

    filename = tmpdir_factory.mktemp('data').join('invalid_classname.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="this is not a valid classname" file="tests/test_default.py" line="8"
            name="test_pass[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_properties=default_testcase_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def test_without_test_step(tmpdir_factory,
                           default_global_properties,
                           default_testcase_elements):
    """An xml example without test_step property"""

    filename = tmpdir_factory.mktemp('data').join('single_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass[ansible://localhost]" time="0.00372695922852">
                <properties>
                        <property name="jira" value="ASC-123"/>
                        <property name="jira" value="ASC-456"/>
                        <property name="test_id" value="1"/>
                        <property name="start_time" value="2018-04-10T21:38:18Z"/>
                        <property name="end_time" value="2018-04-10T21:38:19Z"/>
                    </properties>
                {testcase_elements}
            </testcase>
        </testsuite>
        """.format(global_properties=default_global_properties,
                   testcase_elements=default_testcase_elements)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename
