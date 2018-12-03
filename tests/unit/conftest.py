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
def tempest_xml(tmpdir_factory):
    """The first example of tempest xml results"""
    filename = tmpdir_factory.mktemp('data').join('tempest.xml').strpath
    junit_xml = \
        """
        <testsuite errors="0" failures="0" name="" tests="122" time="183.872">
            <testcase classname="tempest.api.identity.admin.v3.test_domains.DefaultDomainTestJSON" name="test_default_domain_exists[id-17a5de24-e6a0-4e4a-a9ee-d85b6e5612b5,smoke]" time="0.029"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domain_configuration.DomainConfigurationTestJSON" name="test_create_domain_config_and_show_config_groups_and_options[id-9e3ff13c-f597-4f01-9377-d6c06c2a1477]" time="0.726"/>
            <testcase classname="tempest.api.identity.admin.v3.test_credentials.CredentialsTestJSON" name="test_credentials_create_get_update_delete[id-7cd59bf9-bda4-4c72-9467-d21cab278355,smoke]" time="0.222"/>
            <testcase classname="tempest.api.identity.admin.v3.test_credentials.CredentialsTestJSON" name="test_credentials_list_delete[id-13202c00-0021-42a1-88d4-81b44d448aab]" time="0.199"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domain_configuration.DomainConfigurationTestJSON" name="test_create_update_and_delete_domain_config[id-7161023e-5dd0-4612-9da0-1bac6ac30b63]" time="0.620"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domain_configuration.DomainConfigurationTestJSON" name="test_create_update_and_delete_domain_config_groups_and_opts[id-c7510fa2-6661-4170-9c6b-4783a80651e9]" time="1.054"/>
            <testcase classname="tempest.api.identity.admin.v3.test_default_project_id.TestDefaultProjectId" name="test_default_project_id[id-d6110661-6a71-49a7-a453-b5e26640ff6d]" time="3.013"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domain_configuration.DomainConfigurationTestJSON" name="test_show_default_group_config_and_options[id-11a02bf0-6f94-4380-b3b0-c8dc18fc0d22]" time="1.353"/>
            <testcase classname="tempest.api.identity.admin.v3.test_endpoints.EndPointsTestJSON" name="test_create_list_show_delete_endpoint[id-0e2446d2-c1fd-461b-a729-b9e73e3e3b37]" time="0.308"/>
            <testcase classname="tempest.api.identity.admin.v3.test_endpoints.EndPointsTestJSON" name="test_list_endpoints[id-c19ecf90-240e-4e23-9966-21cee3f6a618]" time="0.111"/>
            <testcase classname="tempest.api.identity.admin.v3.test_endpoints.EndPointsTestJSON" name="test_update_endpoint[id-37e8f15e-ee7c-4657-a1e7-f6b61e375eff,smoke]" time="0.236"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains.DomainsTestJSON" name="test_create_domain_with_disabled_status[id-036df86e-bb5d-42c0-a7c2-66b9db3a6046]" time="0.208"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains.DomainsTestJSON" name="test_create_domain_without_description[id-2abf8764-309a-4fa9-bc58-201b799817ad]" time="0.474"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains_negative.DomainsNegativeTestJSON" name="test_create_domain_with_empty_name[id-9018461d-7d24-408d-b3fe-ae37e8cd5c9e,negative]" time="0.018"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains_negative.DomainsNegativeTestJSON" name="test_create_domain_with_name_length_over_64[id-37b1bbf2-d664-4785-9a11-333438586eae,negative]" time="0.018"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains.DomainsTestJSON" name="test_create_update_delete_domain[id-f2f5b44a-82e8-4dad-8084-0661ea3b18cf,smoke]" time="0.606"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains_negative.DomainsNegativeTestJSON" name="test_delete_active_domain[gate,id-1f3fbff5-4e44-400d-9ca1-d953f05f609b,negative]" time="0.595"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains_negative.DomainsNegativeTestJSON" name="test_delete_non_existent_domain[id-43781c07-764f-4cf2-a405-953c1916f605,negative]" time="0.111"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains_negative.DomainsNegativeTestJSON" name="test_domain_create_duplicate[id-e6f9e4a2-4f36-4be8-bdbc-4e199ae29427,negative]" time="0.657"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains.DomainsTestJSON" name="test_domain_delete_cascades_content[id-d8d318b7-d1b3-4c37-94c5-3c5ba0b121ea]" time="1.324"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains.DomainsTestJSON" name="test_list_domains[id-8cf516ef-2114-48f1-907b-d32726c734d4]" time="0.029"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains.DomainsTestJSON" name="test_list_domains_filter_by_enabled[id-3fd19840-65c1-43f8-b48c-51bdd066dff9]" time="0.090"/>
            <testcase classname="tempest.api.identity.admin.v3.test_list_projects.ListProjectsTestJSON" name="test_list_projects[id-1d830662-22ad-427c-8c3e-4ec854b0af44]" time="0.330"/>
            <testcase classname="tempest.api.identity.admin.v3.test_domains.DomainsTestJSON" name="test_list_domains_filter_by_name[id-c6aee07b-4981-440c-bb0b-eb598f58ffe9]" time="0.034"/>
            <testcase classname="tempest.api.identity.admin.v3.test_list_projects.ListProjectsTestJSON" name="test_list_projects_with_domains[id-fab13f3c-f6a6-4b9f-829b-d32fd44fdf10]" time="0.087"/>
            <testcase classname="tempest.api.identity.admin.v3.test_list_projects.ListProjectsTestJSON" name="test_list_projects_with_enabled[id-0fe7a334-675a-4509-b00e-1c4b95d5dae8]" time="0.053"/>
            <testcase classname="tempest.api.identity.admin.v3.test_list_projects.ListProjectsTestJSON" name="test_list_projects_with_name[id-fa178524-4e6d-4925-907c-7ab9f42c7e26]" time="0.028"/>
            <testcase classname="tempest.api.identity.admin.v3.test_list_projects.ListProjectsTestJSON" name="test_list_projects_with_parent[id-6edc66f5-2941-4a17-9526-4073311c1fac]" time="0.032"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_associate_user_to_project[id-59398d4a-5dc5-4f86-9a4c-c26cc804d6c6]" time="0.986"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_create_is_domain_project[id-a7eb9416-6f9b-4dbb-b71b-7f73aaef59d5]" time="0.510"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_project_create_enabled[id-1f66dc76-50cc-4741-a200-af984509e480]" time="0.236"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_project_create_not_enabled[id-78f96a9c-e0e0-4ee6-a3ba-fbf6dfd03207]" time="0.163"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_project_create_with_description[id-0ecf465c-0dc4-4532-ab53-91ffeb74d12d]" time="0.189"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_project_create_with_domain[id-5f50fe07-8166-430b-a882-3b2ee0abe26f]" time="0.598"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_project_create_with_parent[id-1854f9c0-70bc-4d11-a08a-1c789d339e3d]" time="0.852"/>
            <testcase classname="tempest.api.identity.admin.v3.test_inherits.InheritsV3TestJSON" name="test_inherit_assign_check_revoke_roles_on_projects_group[id-26021436-d5a4-4256-943c-ded01e0d4b45]" time="0.466"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_project_get_equals_list[id-d1db68b6-aebe-4fa0-b79d-d724d2e21162]" time="0.351"/>
            <testcase classname="tempest.api.identity.admin.v3.test_inherits.InheritsV3TestJSON" name="test_inherit_assign_check_revoke_roles_on_projects_user[id-18b70e45-7687-4b72-8277-b8f1a47d7591]" time="0.309"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_project_update_desc[id-f138b715-255e-4a7d-871d-351e1ef2e153]" time="0.280"/>
            <testcase classname="tempest.api.identity.admin.v3.test_inherits.InheritsV3TestJSON" name="test_inherit_assign_list_check_revoke_roles_on_domains_group[id-c7a8dda2-be50-4fb4-9a9c-e830771078b1]" time="0.225"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_project_update_enable[id-b6b25683-c97f-474d-a595-55d410b68100]" time="0.300"/>
            <testcase classname="tempest.api.identity.admin.v3.test_inherits.InheritsV3TestJSON" name="test_inherit_assign_list_check_revoke_roles_on_domains_user[id-4e6f0366-97c8-423c-b2be-41eae6ac91c8]" time="0.357"/>
            <testcase classname="tempest.api.identity.admin.v3.test_endpoint_groups.EndPointGroupsTest" name="test_create_list_show_check_delete_endpoint_group[id-7c69e7a1-f865-402d-a2ea-44493017315a]" time="0.286"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON" name="test_project_update_name[id-f608f368-048c-496b-ad63-d286c26dab6b]" time="0.360"/>
            <testcase classname="tempest.api.identity.admin.v3.test_endpoint_groups.EndPointGroupsTest" name="test_update_endpoint_group[id-51c8fc38-fa84-4e76-b5b6-6fc37770fb26]" time="0.186"/>
            <testcase classname="tempest.api.identity.admin.v3.test_list_users.UsersV3TestJSON" name="test_get_user[id-b4baa3ae-ac00-4b4e-9e27-80deaad7771f]" time="0.129"/>
            <testcase classname="tempest.api.identity.admin.v3.test_list_users.UsersV3TestJSON" name="test_list_user_domains[id-08f9aabb-dcfe-41d0-8172-82b5fa0bd73d]" time="0.120"/>
            <testcase classname="tempest.api.identity.admin.v3.test_list_users.UsersV3TestJSON" name="test_list_users[id-b30d4651-a2ea-4666-8551-0c0e49692635]" time="0.049"/>
            <testcase classname="tempest.api.identity.admin.v3.test_list_users.UsersV3TestJSON" name="test_list_users_with_name[id-c285bb37-7325-4c02-bff3-3da5d946d683]" time="0.057"/>
            <testcase classname="tempest.api.identity.admin.v3.test_list_users.UsersV3TestJSON" name="test_list_users_with_not_enabled[id-bff8bf2f-9408-4ef5-b63a-753c8c2124eb]" time="0.035"/>
            <testcase classname="tempest.api.identity.admin.v3.test_inherits.InheritsV3TestJSON" name="test_inherit_assign_list_revoke_user_roles_on_domain[id-3acf666e-5354-42ac-8e17-8b68893bcd36]" time="0.921"/>
            <testcase classname="tempest.api.identity.admin.v3.test_inherits.InheritsV3TestJSON" name="test_inherit_assign_list_revoke_user_roles_on_project_tree[id-9f02ccd9-9b57-46b4-8f77-dd5a736f3a06]" time="0.715"/>
            <testcase classname="tempest.api.identity.admin.v3.test_endpoints_negative.EndpointsNegativeTestJSON" name="test_create_with_enabled_False[id-ac6c137e-4d3d-448f-8c83-4f13d0942651,negative]" time="0.017"/>
            <testcase classname="tempest.api.identity.admin.v3.test_endpoints_negative.EndpointsNegativeTestJSON" name="test_create_with_enabled_True[id-9c43181e-0627-484a-8c79-923e8a59598b,negative]" time="0.018"/>
            <testcase classname="tempest.api.identity.admin.v3.test_endpoints_negative.EndpointsNegativeTestJSON" name="test_update_with_enabled_False[id-65e41f32-5eb7-498f-a92a-a6ccacf7439a,negative]" time="0.117"/>
            <testcase classname="tempest.api.identity.admin.v3.test_endpoints_negative.EndpointsNegativeTestJSON" name="test_update_with_enabled_True[id-faba3587-f066-4757-a48e-b4a3f01803bb,negative]" time="0.119"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_assignments_for_domain_roles[id-3859df7e-5b78-4e4d-b10e-214c8953842a]" time="0.358"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects_negative.ProjectsNegativeTestJSON" name="test_create_project_by_unauthorized_user[id-8fba9de2-3e1f-4e77-812a-60cb68f8df13,negative]" time="0.124"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects_negative.ProjectsNegativeTestJSON" name="test_create_project_with_empty_name[id-7828db17-95e5-475b-9432-9a51b4aa79a9,negative]" time="0.021"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects_negative.ProjectsNegativeTestJSON" name="test_create_projects_name_length_over_64[id-502b6ceb-b0c8-4422-bf53-f08fdb21e2f0,negative]" time="0.017"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects_negative.ProjectsNegativeTestJSON" name="test_delete_non_existent_project[id-7965b581-60c1-43b7-8169-95d4ab7fc6fb,negative]" time="0.031"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects_negative.ProjectsNegativeTestJSON" name="test_list_projects_by_unauthorized_user[id-24c49279-45dd-4155-887a-cb738c2385aa,negative]" time="0.016"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_assignments_for_implied_roles_create_delete[id-c8828027-df48-4021-95df-b65b92c7429e]" time="0.358"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects_negative.ProjectsNegativeTestJSON" name="test_project_create_duplicate[id-874c3e84-d174-4348-a16b-8c01f599561b,negative]" time="0.252"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_domain_roles_create_delete[id-d92a41d2-5501-497a-84bb-6e294330e8f8]" time="0.199"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_grant_list_revoke_role_to_group_on_domain[id-4bf8a70b-e785-413a-ad53-9f91ce02faa7]" time="0.144"/>
            <testcase classname="tempest.api.identity.admin.v3.test_projects_negative.ProjectsNegativeTestJSON" name="test_project_delete_by_unauthorized_user[id-8d68c012-89e0-4394-8d6b-ccd7196def97,negative]" time="0.341"/>
            <testcase classname="tempest.api.identity.admin.v3.test_oauth_consumers.OAUTHConsumersV3Test" name="test_create_and_show_consumer[id-c8307ea6-a86c-47fd-ae7b-5b3b2caca76d]" time="0.158"/>
            <testcase classname="tempest.api.identity.admin.v3.test_oauth_consumers.OAUTHConsumersV3Test" name="test_delete_consumer[id-fdfa1b7f-2a31-4354-b2c7-f6ae20554f93]" time="0.366"/>
            <testcase classname="tempest.api.identity.admin.v3.test_oauth_consumers.OAUTHConsumersV3Test" name="test_list_consumers[id-09ca50de-78f2-4ffb-ac71-f2254036b2b8]" time="0.233"/>
            <testcase classname="tempest.api.identity.admin.v3.test_oauth_consumers.OAUTHConsumersV3Test" name="test_update_consumer[id-080a9b1a-c009-47c0-9979-5305bf72e3dc]" time="0.211"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_grant_list_revoke_role_to_group_on_project[id-cbf11737-1904-4690-9613-97bcbb3df1c4]" time="1.186"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_grant_list_revoke_role_to_user_on_domain[id-6c9a2940-3625-43a3-ac02-5dcec62ef3bd]" time="0.346"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_grant_list_revoke_role_to_user_on_project[id-c6b80012-fe4a-498b-9ce8-eb391c05169f]" time="0.265"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_implied_domain_roles[id-eb1e1c24-1bc4-4d47-9748-e127a1852c82]" time="1.128"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_implied_roles_create_check_show_delete[id-c90c316c-d706-4728-bcba-eb1912081b69]" time="0.192"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_list_all_implied_roles[id-3748c316-c18f-4b08-997b-c60567bc6235]" time="0.233"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_list_roles[id-f5654bcc-08c4-4f71-88fe-05d64e06de94]" time="0.022"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_role_create_update_show_list[id-18afc6c0-46cf-4911-824e-9989cc056c3a,smoke]" time="0.188"/>
            <testcase classname="tempest.api.identity.admin.v3.test_roles.RolesV3TestJSON" name="test_roles_hierarchy[id-dc6f5959-b74d-4e30-a9e5-a8255494ff00]" time="0.284"/>
            <testcase classname="tempest.api.identity.admin.v3.test_groups.GroupsV3TestJSON" name="test_group_create_update_get[id-2e80343b-6c81-4ac3-88c7-452f3e9d5129]" time="0.262"/>
            <testcase classname="tempest.api.identity.admin.v3.test_groups.GroupsV3TestJSON" name="test_group_update_with_few_fields[id-b66eb441-b08a-4a6d-81ab-fef71baeb26c]" time="0.226"/>
            <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_get_user[id-c10dcd90-461d-4b16-8e23-4eb836c00644]" time="0.869"/>
            <testcase classname="tempest.api.identity.admin.v3.test_regions.RegionsTestJSON" name="test_create_region_with_specific_id[id-2c12c5b5-efcf-4aa5-90c5-bff1ab0cdbe2,smoke]" time="0.090"/>
            <testcase classname="tempest.api.identity.admin.v3.test_regions.RegionsTestJSON" name="test_create_update_get_delete_region[id-56186092-82e4-43f2-b954-91013218ba42]" time="0.332"/>
            <testcase classname="tempest.api.identity.admin.v3.test_regions.RegionsTestJSON" name="test_list_regions[id-d180bf99-544a-445c-ad0d-0c0d27663796]" time="0.019"/>
            <testcase classname="tempest.api.identity.admin.v3.test_regions.RegionsTestJSON" name="test_list_regions_filter_by_parent_region_id[id-2d1057cb-bbde-413a-acdf-e2d265284542]" time="0.121"/>
            <testcase classname="tempest.api.identity.admin.v3.test_groups.GroupsV3TestJSON" name="test_group_users_add_list_delete[id-1598521a-2f36-4606-8df9-30772bd51339,smoke]" time="2.828"/>
            <testcase classname="tempest.api.identity.admin.v3.test_groups.GroupsV3TestJSON" name="test_list_groups[id-cc9a57a5-a9ed-4f2d-a29f-4f979a06ec71]" time="0.396"/>
            <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_list_user_projects[id-a831e70c-e35b-430b-92ed-81ebbc5437b8]" time="2.098"/>
            <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_password_history_not_enforced_in_admin_reset[id-568cd46c-ee6c-4ab4-a33a-d3791931979e]" time="0.000">
                <skipped>Security compliance not available.</skipped>
            </testcase>
            <testcase classname="tempest.api.identity.admin.v3.test_groups.GroupsV3TestJSON" name="test_list_user_groups[id-64573281-d26a-4a52-b899-503cb0f4e4ec]" time="1.230"/>
            <testcase classname="" name="setUpClass (tempest.api.identity.admin.v3.test_trusts.TrustsV3TestJSON)" time="0.000">
                <skipped>Trusts aren't enabled</skipped>
            </testcase>
            <testcase classname="tempest.api.identity.admin.v3.test_services.ServicesTestJSON" name="test_create_service_without_description[id-d1dcb1a1-2b6b-4da8-bbb8-5532ef6e8269]" time="0.087"/>
            <testcase classname="tempest.api.identity.admin.v3.test_services.ServicesTestJSON" name="test_create_update_get_service[id-5193aad5-bcb7-411d-85b0-b3b61b96ef06,smoke]" time="0.378"/>
            <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_update_user_password[id-2d223a0e-e457-4a70-9fb1-febe027a0ff9]" time="2.958"/>
            <testcase classname="tempest.api.identity.admin.v3.test_services.ServicesTestJSON" name="test_list_services[id-e55908e8-360e-439e-8719-c3230a3e179e]" time="0.587"/>
            <testcase classname="tempest.api.identity.admin.v3.test_users.UsersV3TestJSON" name="test_user_update[id-b537d090-afb9-4519-b95d-270b0708e87e]" time="1.318"/>
            <testcase classname="tempest.api.identity.admin.v3.test_users_negative.UsersNegativeTest" name="test_authentication_for_disabled_user[id-b3c9fccc-4134-46f5-b600-1da6fb0a3b1f,negative]" time="1.580"/>
            <testcase classname="tempest.api.identity.admin.v3.test_users_negative.UsersNegativeTest" name="test_create_user_for_non_existent_domain[id-e75f006c-89cc-477b-874d-588e4eab4b17,negative]" time="0.026"/>
            <testcase classname="tempest.api.identity.admin.v3.test_policies.PoliciesTestJSON" name="test_create_update_delete_policy[id-e544703a-2f03-4cf2-9b0f-350782fdb0d3,smoke]" time="0.258"/>
            <testcase classname="tempest.api.identity.admin.v3.test_policies.PoliciesTestJSON" name="test_list_policies[id-1a0ad286-2d06-4123-ab0d-728893a76201]" time="0.403"/>
            <testcase classname="tempest.api.identity.v3.test_users.IdentityV3UsersTest" name="test_password_history_check_self_service_api[id-941784ee-5342-4571-959b-b80dd2cea516]" time="0.000">
                <skipped>Security compliance not available.</skipped>
            </testcase>
            <testcase classname="tempest.api.identity.v3.test_users.IdentityV3UsersTest" name="test_user_account_lockout[id-a7ad8bbf-2cff-4520-8c1d-96332e151658]" time="0.000">
                <skipped>Security compliance not available.</skipped>
            </testcase>
            <testcase classname="tempest.api.identity.v3.test_projects.IdentityV3ProjectsTest" name="test_list_projects_returns_only_authorized_projects[id-86128d46-e170-4644-866a-cc487f699e1d]" time="1.073"/>
            <testcase classname="tempest.api.identity.v3.test_catalog.IdentityCatalogTest" name="test_catalog_standardization[id-56b57ced-22b8-4127-9b8a-565dfb0207e2]" time="0.019"/>
            <testcase classname="tempest.api.identity.v3.test_tokens.TokensV3Test" name="test_create_token[id-6f8e4436-fc96-4282-8122-e41df57197a9]" time="0.377"/>
            <testcase classname="tempest.api.identity.v3.test_tokens.TokensV3Test" name="test_validate_token[id-a9512ac3-3909-48a4-b395-11f438e16260]" time="0.621"/>
            <testcase classname="tempest.api.identity.v3.test_users.IdentityV3UsersTest" name="test_user_update_own_password[id-ad71bd23-12ad-426b-bb8b-195d2b635f27]" time="7.666"/>
            <testcase classname="tempest.api.identity.admin.v3.test_tokens.TokensV3TestJSON" name="test_get_available_domain_scopes[id-ec5ecb05-af64-4c04-ac86-4d9f6f12f185]" time="3.513"/>
            <testcase classname="tempest.api.identity.admin.v3.test_tokens.TokensV3TestJSON" name="test_get_available_project_scopes[id-08ed85ce-2ba8-4864-b442-bcc61f16ae89]" time="0.229"/>
            <testcase classname="tempest.api.identity.admin.v3.test_tokens.TokensV3TestJSON" name="test_rescope_token[id-565fa210-1da1-4563-999b-f7b5b67cf112]" time="2.027"/>
            <testcase classname="tempest.api.identity.admin.v3.test_tokens.TokensV3TestJSON" name="test_tokens[id-0f9f5a5f-d5cd-4a86-8a5b-c5ded151f212]" time="1.150"/>
            <testcase classname="tempest.scenario.test_object_storage_basic_ops.TestObjectStorageBasicOps" name="test_swift_acl_anonymous_download[id-916c7111-cb1f-44b2-816d-8f760e4ea910,object_storage,slow]" time="1.365"/>
            <testcase classname="tempest.scenario.test_object_storage_basic_ops.TestObjectStorageBasicOps" name="test_swift_basic_ops[id-b920faf1-7b8a-4657-b9fe-9c4512bfb381,object_storage]" time="0.227"/>
            <testcase classname="tempest.api.identity.v3.test_api_discovery.TestApiDiscovery" name="test_api_media_types[id-657c1970-4722-4189-8831-7325f3bc4265,smoke]" time="0.076"/>
            <testcase classname="tempest.api.identity.v3.test_api_discovery.TestApiDiscovery" name="test_api_version_resources[id-b9232f5e-d9e5-4d97-b96c-28d3db4de1bd,smoke]" time="0.076"/>
            <testcase classname="tempest.api.identity.v3.test_api_discovery.TestApiDiscovery" name="test_api_version_statuses[id-8879a470-abfb-47bb-bb8d-5a7fd279ad1e,smoke]" time="0.015"/>
            <testcase classname="tempest.api.identity.v3.test_api_discovery.TestApiDiscovery" name="test_list_api_versions[id-721f480f-35b6-46c7-846e-047e6acea0dc,smoke]" time="0.008"/>
            <testcase classname="tempest.api.volume.admin.test_volumes_backup.VolumesBackupsAdminTest" name="test_volume_backup_export_import[id-a99c54a1-dd80-4724-8a13-13bf58d4068d]" time="49.289"/>
            <testcase classname="tempest.api.volume.admin.test_volumes_backup.VolumesBackupsAdminTest" name="test_volume_backup_reset_status[id-47a35425-a891-4e13-961c-c45deea21e94]" time="27.117"/>
            <testcase classname="tempest.scenario.test_server_basic_ops.TestServerBasicOps" name="test_server_basic_ops[compute,id-7fff3fb3-91d8-4fd0-bd7d-0204f1f180ba,network,smoke]" time="38.366"/>
        </testsuite>
        """

    with open(filename, 'w') as f:
        f.write(junit_xml)

    return filename
