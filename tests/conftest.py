# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest


# ======================================================================================================================
# Globals
# ======================================================================================================================
DEFAULT_GLOBAL_PROPERTIES = \
    """
            <properties>
                <property name="BUILD_URL" value="Unknown"/>
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
    """

DEFAULT_TESTCASE_PROPERTIES = \
    """
                <properties>
                    <property name="test_id" value="1"/>
                    <property name="start_time" value="2018-04-10T21:38:18Z"/>
                    <property name="end_time" value="2018-04-10T21:38:19Z"/>
                </properties>
    """


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
def suite_mix_status_xml(tmpdir_factory):
    """JUnitXML sample representing mixed status for multiple test cases in a test suite."""

    filename = tmpdir_factory.mktemp('data').join('suite_mix_status.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="1" failures="1" name="pytest" skips="1" tests="4" time="1.853">
            {global_properties}
            <testcase classname="tests.test_default.TestClass" file="tests/test_default.py" line="35"
            name="test_pass[ansible://localhost]" time="0.00357985496521">
                {testcase_properties}
            </testcase>
            <testcase classname="tests.test_default.TestClass" file="tests/test_default.py" line="38"
            name="test_fail[ansible://localhost]" time="0.00310778617859">
                {testcase_properties}
                <failure message="assert False">self = &lt;test_default.TestClass object at 0x7fb9c7b9a790&gt;
        host = &lt;testinfra.host.Host object at 0x7fb9c7c18d10&gt;

            def test_fail(self, host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:40: AssertionError</failure>
            </testcase>
            <testcase classname="tests.test_default.TestClass" file="tests/test_default.py" line="41"
            name="test_error[ansible://localhost]" time="0.00223517417908">
                {testcase_properties}
                <error message="test setup failure">self = &lt;test_default.TestClass object at 0x7fb9cb5b7190&gt;
        host = &lt;testinfra.host.Host object at 0x7fb9c7c18d10&gt;

            @pytest.fixture
            def error_fixture(self, host):
        &gt;       raise RuntimeError(&apos;oops&apos;)
        E       RuntimeError: oops

        tests/test_default.py:34: RuntimeError</error>
            </testcase>
            <testcase classname="tests.test_default.TestClass" file="tests/test_default.py" line="44"
            name="test_skip[ansible://localhost]" time="0.00199604034424">
                {testcase_properties}
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:44: &lt;py._xmlgen.raw object at 0x7fb9c904d190&gt;
                </skipped>
            </testcase>
        </testsuite>
        """.format(global_properties=DEFAULT_GLOBAL_PROPERTIES, testcase_properties=DEFAULT_TESTCASE_PROPERTIES)

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def bad_xml(tmpdir_factory):
    """JUnitXML sample representing all passing tests."""

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
