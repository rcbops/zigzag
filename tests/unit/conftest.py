# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from lxml import etree
import pytest
pytest_plugins = ['pytester']

# ======================================================================================================================
# Globals
# ======================================================================================================================
DEFAULT_GLOBAL_PROPERTIES = \
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

DEFAULT_TESTCASE_PROPERTIES = \
    """
                <properties>
                    <property name="jira" value="ASC-123"/>
                    <property name="jira" value="ASC-456"/>
                    <property name="test_id" value="1"/>
                    <property name="start_time" value="2018-04-10T21:38:18Z"/>
                    <property name="end_time" value="2018-04-10T21:38:19Z"/>
                </properties>
    """


# ======================================================================================================================
# Helpers
# ======================================================================================================================
# noinspection PyUnresolvedReferences
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


def is_sub_dict(small, big):
    """Determine if one dictionary is a subset of another dictionary.

    Args:
        small (dict): A dictionary that is proposed to be a subset of another dictionary.
        big (dict): A dictionary that is a superset of another dictionary.

    Returns:
        bool: A bool indicating if the small dictionary is in fact a sub-dictionary of big
    """

    return dict(big, **small) == big


def run_and_parse(testdir, exit_code_exp=0, runpytest_args=list()):
    """Execute a pytest run against a directory containing pytest Python files.

    Args:
        testdir (_pytest.pytester.TestDir): A pytest fixture for testing pytest plug-ins.
        exit_code_exp (int): The expected exit code for pytest run. (Default = 0)
        runpytest_args (list(object)): A list of positional arguments to pass into the "testdir" fixture.
            (Default = [])

    Returns:
        JunitXml: A wrapper class for the etree element at the root of the supplied JUnitXML file.
    """

    result_path = testdir.tmpdir.join('junit.xml')
    result = testdir.runpytest("--junitxml={}".format(result_path), *runpytest_args)

    assert result.ret == exit_code_exp

    junit_xml_doc = JunitXml(str(result_path))

    return junit_xml_doc


def run_and_parse_with_config(testdir, config, exit_code_exp=0, runpytest_args=list()):
    """Execute a pytest run against a directory containing pytest Python files.

    Args:
        testdir (_pytest.pytester.TestDir): A pytest fixture for testing pytest plug-ins.
        config (str): THe contents of the config that you want to use.
        exit_code_exp (int): The expected exit code for pytest run. (Default = 0)
        runpytest_args (list(object)): A list of positional arguments to pass into the "testdir" fixture.
            (Default = [])

    Returns:
        JunitXml: A wrapper class for the etree element at the root of the supplied JUnitXML file.
    """

    result_path = testdir.tmpdir.join('junit.xml')
    config_path = testdir.tmpdir.join('conf.conf')
    with open(str(config_path), 'w') as f:
        f.write(config)

    result = testdir.runpytest("--junitxml={}".format(result_path), "-c={}".format(config_path), *runpytest_args)

    assert result.ret == exit_code_exp

    junit_xml_doc = JunitXml(str(result_path))

    return junit_xml_doc


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
@pytest.fixture(scope='session')
def single_passing_xml(tmpdir_factory):
    """JUnitXML sample representing a single passing test."""

    filename = tmpdir_factory.mktemp('data').join('single_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
            </testcase>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def single_fail_xml(tmpdir_factory):
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
            </testcase>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def single_error_xml(tmpdir_factory):
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
            </testcase>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def single_skip_xml(tmpdir_factory):
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
            </testcase>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def flat_all_passing_xml(tmpdir_factory):
    """JUnitXML sample representing multiple passing test cases."""

    filename = tmpdir_factory.mktemp('data').join('flat_all_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass1[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="12"
            name="test_pass2[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="15"
            name="test_pass3[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="18"
            name="test_pass4[ansible://localhost]" time="0.00314617156982">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="21"
            name="test_pass5[ansible://localhost]" time="0.00332307815552">
                {testcase_properties}
            </testcase>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def suite_all_passing_xml(tmpdir_factory):
    """JUnitXML sample representing multiple passing test cases in a test suite. (Tests within a Python class)"""

    filename = tmpdir_factory.mktemp('data').join('suite_all_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
            <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default.TestSuite" file="tests/test_default.py" line="8"
            name="test_pass1[ansible://localhost]" time="0.00372695922852">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default.TestSuite" file="tests/test_default.py" line="12"
            name="test_pass2[ansible://localhost]" time="0.00341415405273">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default.TestSuite" file="tests/test_default.py" line="15"
            name="test_pass3[ansible://localhost]" time="0.00363945960999">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default.TestSuite" file="tests/test_default.py" line="18"
            name="test_pass4[ansible://localhost]" time="0.00314617156982">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default.TestSuite" file="tests/test_default.py" line="21"
            name="test_pass5[ansible://localhost]" time="0.00332307815552">
                {testcase_properties}
            </testcase>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def flat_mix_status_xml(tmpdir_factory):
    """JUnitXML sample representing mixed status for multiple test cases."""

    filename = tmpdir_factory.mktemp('data').join('flat_mix_status.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="1" failures="1" name="pytest" skips="1" tests="4" time="1.901">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="12"
            name="test_pass[ansible://localhost]" time="0.0034921169281">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                {testcase_properties}
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
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
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="24"
            name="test_skip[ansible://localhost]" time="0.00197100639343">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
            </testcase>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

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
def missing_testcase_properties_xml(tmpdir_factory):
    """JUnitXML sample representing a test case that is missing the test case "properties" element."""

    filename = tmpdir_factory.mktemp('data').join('missing_testcase_properties.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            {global_properties}
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass[ansible://localhost]" time="0.00372695922852"/>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def missing_test_id_xml(tmpdir_factory):
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
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def missing_build_url_xml(tmpdir_factory):
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
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def classname_with_dashes_xml(tmpdir_factory):
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
            </testcase>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def invalid_classname_xml(tmpdir_factory):
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
            </testcase>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def testsuite_attribs_exp():
    """A common set of testsuite attributes shared across many test cases."""

    return {'tests': '1', 'errors': '0', 'name': 'pytest', 'skips': '0', 'failures': '0'}


@pytest.fixture(scope='session')
def undecorated_test_function():
    """An undecorated Python function that simple passes with the following named formatters:

        test_name: Name of undecorated function.
    """

    py_file = \
        """
        import pytest
        def {test_name}():
            pass
        """

    return py_file


@pytest.fixture(scope='session')
def single_decorated_test_function():
    """An Python function decorated with a single pytest mark with the following named formatters:

        test_name: Name of decorated function.
        mark_type: The name of the pytest mark.
        mark_arg: The value for the pytest mark.
    """

    py_file = \
        """
        import pytest
        @pytest.mark.{mark_type}('{mark_arg}')
        def {test_name}():
            pass
        """

    return py_file


@pytest.fixture(scope='session')
def properly_decorated_test_function():
    """An Python function decorated with the required 'test_id' and 'jira' marks along with the following named
    formatters:

        test_name: Name of decorated function.
        test_id: The desired 'test_id' mark argument.
        jira_id: The desired 'jira' mark argument.
    """

    py_file = \
        """
        import pytest
        @pytest.mark.test_id('{test_id}')
        @pytest.mark.jira('{jira_id}')
        def {test_name}():
            pass
        """

    return py_file


@pytest.fixture(scope='session')
def sleepy_test_function():
    """An Python function that sleeps for a period of time with the following named formatters:

        test_name: Name of decorated function.
        seconds: The number of seconds to sleep.
    """

    py_file = \
        """
        import pytest
        import time
        def {test_name}():
            time.sleep({seconds})
        """

    return py_file


# ======================================================================================================================
# Classes
# ======================================================================================================================
class JunitXml(object):
    """A helper class for obtaining elements from JUnitXML result files produced by pytest-rpc."""

    def __init__(self, xml_file_path):
        """Create a JunitXML class object.

        Args:
            xml_file_path (str): A file path to a JUnitXML file created using the pytest-rpc plug-in.
        """

        self._xml_file_path = xml_file_path
        self._xml_doc = etree.parse(xml_file_path).getroot()

        self._testsuite_props = None
        self._testsuite_attribs = None

    @property
    def testsuite_props(self):
        """dict: A dictionary of properties on the testsuite root element."""

        if not self._testsuite_props:
            self._testsuite_props = {p.attrib['name']: p.attrib['value']
                                     for p in self._xml_doc.findall('./properties/property')}

        return self._testsuite_props

    @property
    def testsuite_attribs(self):
        """dict: A dictionary of attributes on the testsuite root element."""

        if not self._testsuite_attribs:
            self._testsuite_attribs = dict(self._xml_doc.attrib)

        return self._testsuite_attribs

    @property
    def xml_doc(self):
        """lxml.etree.Element: Raw etree doc at the testsuite root element."""

        return self._xml_doc

    def get_testcase_property(self, testcase_name, property_name):
        """Retrieve all the properties for a specified testcase.

        Args:
            testcase_name (str): The name of the desired testcase from which to retrieve properties.
            property_name (str): The name of the desired property.

        Returns:
            list: A list of values for the specified property name.
        """

        xpath = "./testcase/[@name='{}']/properties/property/[@name='{}']".format(testcase_name, property_name)

        return [p.attrib['value'] for p in self._xml_doc.findall(xpath)]

    def get_testcase_properties(self, testcase_name):
        """Retrieve all the properties for a specified testcase.

        Note: if there are multiple properties with the same name only one of the values will be returned.

        Args:
            testcase_name (str): The name of the desired testcase from which to retrieve properties.

        Returns:
            dict: A dictionary of properties on the specified testcase element.
        """

        xpath = "./testcase/[@name='{}']/properties/property".format(testcase_name)

        return {p.attrib['name']: p.attrib['value'] for p in self._xml_doc.findall(xpath)}
