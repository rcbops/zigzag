# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
pytest_plugins = ['helpers_namespace', 'tests.helper.fixtures']


# ======================================================================================================================
# Public Fixtures: Meant to be consumed by tests
# ======================================================================================================================
@pytest.fixture(scope='session')
def single_passing_test_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with one passing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_passing_asc.xml', asc_config_file, asc_global_props)
    zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def single_passing_test_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "mk8s" CI environment with one passing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_passing_mk8s.xml', mk8s_config_file, mk8s_global_props)
    zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def single_failing_test_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with one failing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_failing_asc.xml', asc_config_file, asc_global_props)
    zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def single_failing_test_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "mk8s" CI environment with one failing test in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_failing_mk8s.xml', mk8s_config_file, mk8s_global_props)
    zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_passing_tests_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 passing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_passing_asc.xml', asc_config_file, asc_global_props)
    for i in range(3):
        zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_passing_tests_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 passing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_passing_mk8s.xml', mk8s_config_file, mk8s_global_props)
    for i in range(3):
        zz_runner.add_test_case('passed')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_failing_tests_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 failing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_failing_asc.xml', asc_config_file, asc_global_props)
    for i in range(3):
        zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_failing_tests_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 failing tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_failing_mk8s.xml', mk8s_config_file, mk8s_global_props)
    for i in range(3):
        zz_runner.add_test_case('failure')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_erroring_tests_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 erroring tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_erroring_asc.xml', asc_config_file, asc_global_props)
    for i in range(3):
        zz_runner.add_test_case('error')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_erroring_tests_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 erroring tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_erroring_mk8s.xml', mk8s_config_file, mk8s_global_props)
    for i in range(3):
        zz_runner.add_test_case('error')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_skipping_tests_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with 3 skipping tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_skipping_asc.xml', asc_config_file, asc_global_props)
    for i in range(3):
        zz_runner.add_test_case('skipped')

    return zz_runner


@pytest.fixture(scope='session')
def multiple_skipping_tests_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 3 skipping tests in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_skipping_mk8s.xml', mk8s_config_file, mk8s_global_props)
    for i in range(3):
        zz_runner.add_test_case('skipped')

    return zz_runner


@pytest.fixture(scope='session')
def mixed_status_tests_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with 4 tests covering the various test execution
     states in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_mixed_asc.xml', asc_config_file, asc_global_props)
    for state in ('passed', 'failure', 'error', 'skipped'):
        zz_runner.add_test_case(state)

    return zz_runner


@pytest.fixture(scope='session')
def mixed_status_tests_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "mk8s" CI environment with 4 tests covering the various test execution
     states in the JUnitXML file.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('multiple_mixed_mk8s.xml', mk8s_config_file, mk8s_global_props)
    for state in ('passed', 'failure', 'error', 'skipped'):
        zz_runner.add_test_case(state)

    return zz_runner


@pytest.fixture(scope='session')
def single_passing_test_step_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner configured for the "asc" CI environment with a test case containing one passing test step.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_passing_test_step_for_asc.xml', asc_config_file, asc_global_props)
    zz_runner.add_test_case('passed', test_steps=[{'state': 'passed'}])

    return zz_runner


@pytest.fixture(scope='session')
def single_passing_test_step_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner configured for the "mk8s" CI environment with a test case containing one passing test step.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('single_passing_test_step_for_mk8s.xml', mk8s_config_file, mk8s_global_props)
    zz_runner.add_test_case('passed', test_steps=[{'state': 'passed'}])

    return zz_runner


@pytest.fixture(scope='session')
def asc_config_file(tmpdir_factory):
    """A config for zigzag used by the ASC team

    Returns:
        str : a path to a config file
    """

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
                "test_cycle": "{{ ZZ_INTEGRATION_TEST_CYCLE }}",
                "project_id": "{{ ZZ_INTEGRATION_PROJECT_ID }}",
                "module_hierarchy": [
                  "{{ RPC_PRODUCT_RELEASE }}",
                  "{ {RPC_RELEASE }}",
                  "{{ JOB_NAME }}",
                  "{{ MOLECULE_TEST_REPO }}",
                  "{{ zz_testcase_class }}"
                ],
                "path_to_test_exec_dir": "/molecule/default",
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
def mk8s_config_file(tmpdir_factory):
    """A config for zigzag used by the mk8s team

    Returns:
        str : a path to a config file
    """

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
                "test_cycle": "{{ ZZ_INTEGRATION_TEST_CYCLE }}",
                "project_id": "{{ ZZ_INTEGRATION_PROJECT_ID }}",
                "module_hierarchy": [
                  "{{ 'PR' if CHANGE_BRANCH else BRANCH_NAME }}",
                  "{{ zz_testcase_class }}"
                ],
                "path_to_test_exec_dir": "tools/installer",
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
def asc_global_props():
    """The properties collected by the ASC team

    Returns:
        dict : a dictionary with the desired key value pairs
    """
    return {"BUILD_URL": "BUILD_URL",
            "BUILD_NUMBER": "BUILD_NUMBER",
            "RE_JOB_ACTION": "RE_JOB_ACTION",
            "RE_JOB_IMAGE": "RE_JOB_IMAGE",
            "RE_JOB_SCENARIO": "RE_JOB_SCENARIO",
            "RE_JOB_BRANCH": "pike-rc",
            "RPC_RELEASE": "RPC_RELEASE",
            "RPC_PRODUCT_RELEASE": "RPC_PRODUCT_RELEASE",
            "OS_ARTIFACT_SHA": "OS_ARTIFACT_SHA",
            "PYTHON_ARTIFACT_SHA": "PYTHON_ARTIFACT_SHA",
            "APT_ARTIFACT_SHA": "APT_ARTIFACT_SHA",
            "REPO_URL": "https://github.com/rcbops/rpc-openstack",
            "JOB_NAME": "JOB_NAME",
            "MOLECULE_TEST_REPO": "MOLECULE_TEST_REPO",
            "MOLECULE_SCENARIO_NAME": "MOLECULE_SCENARIO_NAME",
            "MOLECULE_GIT_COMMIT": "Unknown"}


@pytest.fixture(scope='session')
def mk8s_global_props():
    """The properties collected by the mk8s team

    Returns:
        dict : a dictionary with the desired key value pairs
    """
    return {"BUILD_URL": "BUILD_URL",
            "BUILD_NUMBER": "BUILD_NUMBER",
            "BUILD_ID": "BUILD_ID",
            "JOB_NAME": "JOB_NAME",
            "BUILD_TAG": "BUILD_TAG",
            "JENKINS_URL": "JENKINS_URL",
            "EXECUTOR_NUMBER": "EXECUTOR_NUMBER",
            "WORKSPACE": "WORKSPACE",
            "CVS_BRANCH": "CVS_BRANCH",
            "GIT_COMMIT": "GIT_COMMIT",
            "GIT_URL": "Unknown",
            "GIT_BRANCH": "master",
            "GIT_LOCAL_BRANCH": "GIT_LOCAL_BRANCH",
            "GIT_AUTHOR_NAME": "GIT_AUTHOR_NAME",
            "GIT_AUTHOR_EMAIL": "GIT_AUTHOR_EMAIL",
            "BRANCH_NAME": "BRANCH_NAME",
            "CHANGE_AUTHOR_DISPLAY_NAME": "CHANGE_AUTHOR_DISPLAY_NAME",
            "CHANGE_AUTHOR": "CHANGE_AUTHOR",
            "CHANGE_BRANCH": "CHANGE_BRANCH",
            "CHANGE_FORK": "CHANGE_FORK",
            "CHANGE_ID": "CHANGE_ID",
            "CHANGE_TARGET": "CHANGE_TARGET",
            "CHANGE_TITLE": "CHANGE_TITLE",
            "CHANGE_URL": "CHANGE_URL",
            "JOB_URL": "JOB_URL",
            "NODE_LABELS": "NODE_LABELS",
            "NODE_NAME": "NODE_NAME",
            "PWD": "PWD",
            "STAGE_NAME": "STAGE_NAME"}
