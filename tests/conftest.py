# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest


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
            <properties>
                <property name="JENKINS_CONSOLE_LOG_URL" value="Unknown"/>
                <property name="SCENARIO" value="Unknown"/>
                <property name="ACTION" value="Unknown"/>
                <property name="IMAGE" value="Unknown"/>
                <property name="OS_ARTIFACT_SHA" value="Unknown"/>
                <property name="PYTHON_ARTIFACT_SHA" value="Unknown"/>
                <property name="APT_ARTIFACT_SHA" value="Unknown"/>
                <property name="GIT_REPO" value="Unknown"/>
                <property name="GIT_BRANCH" value="Unknown"/>
            </properties>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass[ansible://localhost]" time="0.00372695922852">
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
        </testsuite>
        """

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
            <properties>
                <property name="JENKINS_CONSOLE_LOG_URL" value="Unknown"/>
                <property name="SCENARIO" value="Unknown"/>
                <property name="ACTION" value="Unknown"/>
                <property name="IMAGE" value="Unknown"/>
                <property name="OS_ARTIFACT_SHA" value="Unknown"/>
                <property name="PYTHON_ARTIFACT_SHA" value="Unknown"/>
                <property name="APT_ARTIFACT_SHA" value="Unknown"/>
                <property name="GIT_REPO" value="Unknown"/>
                <property name="GIT_BRANCH" value="Unknown"/>
            </properties>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
        </testsuite>
        """

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
            <properties>
                <property name="JENKINS_CONSOLE_LOG_URL" value="Unknown"/>
                <property name="SCENARIO" value="Unknown"/>
                <property name="ACTION" value="Unknown"/>
                <property name="IMAGE" value="Unknown"/>
                <property name="OS_ARTIFACT_SHA" value="Unknown"/>
                <property name="PYTHON_ARTIFACT_SHA" value="Unknown"/>
                <property name="APT_ARTIFACT_SHA" value="Unknown"/>
                <property name="GIT_REPO" value="Unknown"/>
                <property name="GIT_BRANCH" value="Unknown"/>
            </properties>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="20"
            name="test_error[ansible://localhost]" time="0.00208067893982">
                <error message="test setup failure">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            @pytest.fixture
            def error_fixture(host):
        &gt;       raise RuntimeError(&apos;oops&apos;)
        E       RuntimeError: oops

        tests/test_default.py:10: RuntimeError</error>
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
        </testsuite>
        """

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
            <properties>
                <property name="JENKINS_CONSOLE_LOG_URL" value="Unknown"/>
                <property name="SCENARIO" value="Unknown"/>
                <property name="ACTION" value="Unknown"/>
                <property name="IMAGE" value="Unknown"/>
                <property name="OS_ARTIFACT_SHA" value="Unknown"/>
                <property name="PYTHON_ARTIFACT_SHA" value="Unknown"/>
                <property name="APT_ARTIFACT_SHA" value="Unknown"/>
                <property name="GIT_REPO" value="Unknown"/>
                <property name="GIT_BRANCH" value="Unknown"/>
            </properties>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="24"
            name="test_skip[ansible://localhost]" time="0.00197100639343">
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
        </testsuite>
        """

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def flat_all_passing_xml(tmpdir_factory):
    """JUnitXML sample representing all passing tests."""

    filename = tmpdir_factory.mktemp('data').join('flat_all_passing.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="0" failures="0" name="pytest" skips="0" tests="5" time="1.664">
            <properties>
                <property name="JENKINS_CONSOLE_LOG_URL" value="Unknown"/>
                <property name="SCENARIO" value="Unknown"/>
                <property name="ACTION" value="Unknown"/>
                <property name="IMAGE" value="Unknown"/>
                <property name="OS_ARTIFACT_SHA" value="Unknown"/>
                <property name="PYTHON_ARTIFACT_SHA" value="Unknown"/>
                <property name="APT_ARTIFACT_SHA" value="Unknown"/>
                <property name="GIT_REPO" value="Unknown"/>
                <property name="GIT_BRANCH" value="Unknown"/>
            </properties>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="8"
            name="test_pass1[ansible://localhost]" time="0.00372695922852">
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="12"
            name="test_pass2[ansible://localhost]" time="0.00341415405273">
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="15"
            name="test_pass3[ansible://localhost]" time="0.00363945960999">
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="18"
            name="test_pass4[ansible://localhost]" time="0.00314617156982">
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="21"
            name="test_pass5[ansible://localhost]" time="0.00332307815552">
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
        </testsuite>
        """

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def flat_mix_status_xml(tmpdir_factory):
    """JUnitXML sample representing all passing tests."""

    filename = tmpdir_factory.mktemp('data').join('flat_mix_status.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="1" failures="1" name="pytest" skips="1" tests="4" time="1.901">
            <properties>
                <property name="JENKINS_CONSOLE_LOG_URL" value="Unknown"/>
                <property name="SCENARIO" value="Unknown"/>
                <property name="ACTION" value="Unknown"/>
                <property name="IMAGE" value="Unknown"/>
                <property name="OS_ARTIFACT_SHA" value="Unknown"/>
                <property name="PYTHON_ARTIFACT_SHA" value="Unknown"/>
                <property name="APT_ARTIFACT_SHA" value="Unknown"/>
                <property name="GIT_REPO" value="Unknown"/>
                <property name="GIT_BRANCH" value="Unknown"/>
            </properties>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="12"
            name="test_pass[ansible://localhost]" time="0.0034921169281">
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="16"
            name="test_fail[ansible://localhost]" time="0.00335693359375">
                <failure message="assert False">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            def test_fail(host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:18: AssertionError</failure>
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="20"
            name="test_error[ansible://localhost]" time="0.00208067893982">
                <error message="test setup failure">host = &lt;testinfra.host.Host object at 0x7f0921d98cd0&gt;

            @pytest.fixture
            def error_fixture(host):
        &gt;       raise RuntimeError(&apos;oops&apos;)
        E       RuntimeError: oops

        tests/test_default.py:10: RuntimeError</error>
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default" file="tests/test_default.py" line="24"
            name="test_skip[ansible://localhost]" time="0.00197100639343">
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:24: &lt;py._xmlgen.raw object at 0x7f0921ff4d50&gt;
                </skipped>
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
        </testsuite>
        """

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename


@pytest.fixture(scope='session')
def suite_mix_status_xml(tmpdir_factory):
    """JUnitXML sample representing all passing tests."""

    filename = tmpdir_factory.mktemp('data').join('suite_mix_status.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <testsuite errors="1" failures="1" name="pytest" skips="1" tests="4" time="1.853">
            <properties>
                <property name="JENKINS_CONSOLE_LOG_URL" value="Unknown"/>
                <property name="SCENARIO" value="Unknown"/>
                <property name="ACTION" value="Unknown"/>
                <property name="IMAGE" value="Unknown"/>
                <property name="OS_ARTIFACT_SHA" value="Unknown"/>
                <property name="PYTHON_ARTIFACT_SHA" value="Unknown"/>
                <property name="APT_ARTIFACT_SHA" value="Unknown"/>
                <property name="GIT_REPO" value="Unknown"/>
                <property name="GIT_BRANCH" value="Unknown"/>
            </properties>
            <testcase classname="tests.test_default.TestClass" file="tests/test_default.py" line="35"
            name="test_pass[ansible://localhost]" time="0.00357985496521">
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default.TestClass" file="tests/test_default.py" line="38"
            name="test_fail[ansible://localhost]" time="0.00310778617859">
                <failure message="assert False">self = &lt;test_default.TestClass object at 0x7fb9c7b9a790&gt;
        host = &lt;testinfra.host.Host object at 0x7fb9c7c18d10&gt;

            def test_fail(self, host):
        &gt;       assert False
        E       assert False

        tests/test_default.py:40: AssertionError</failure>
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default.TestClass" file="tests/test_default.py" line="41"
            name="test_error[ansible://localhost]" time="0.00223517417908">
                <error message="test setup failure">self = &lt;test_default.TestClass object at 0x7fb9cb5b7190&gt;
        host = &lt;testinfra.host.Host object at 0x7fb9c7c18d10&gt;

            @pytest.fixture
            def error_fixture(self, host):
        &gt;       raise RuntimeError(&apos;oops&apos;)
        E       RuntimeError: oops

        tests/test_default.py:34: RuntimeError</error>
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
            <testcase classname="tests.test_default.TestClass" file="tests/test_default.py" line="44"
            name="test_skip[ansible://localhost]" time="0.00199604034424">
                <skipped message="unconditional skip" type="pytest.skip">
                    tests/test_default.py:44: &lt;py._xmlgen.raw object at 0x7fb9c904d190&gt;
                </skipped>
                <properties>
                    <property name="test_id" value="1"/>
                </properties>
            </testcase>
        </testsuite>
        """

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
    """JUnitXML sample representing all passing tests."""

    filename = tmpdir_factory.mktemp('data').join('bad_junit_root.xml').strpath
    junit_xml = \
        """<?xml version="1.0" encoding="utf-8"?>
        <bad>
        </bad>
        """

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename
