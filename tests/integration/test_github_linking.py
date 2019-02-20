# -*- coding: utf-8 -*-

"""Tests for verifying GitHub linking."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
from zigzag.zigzag_test_log import SWEET_UNICORN_GIF


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
@pytest.fixture(scope='session')
def github_failure_for_asc(_zigzag_runner_factory, asc_config_file, asc_global_props):
    """ZigZag CLI runner with a failing test configured for the "asc" CI environment to create a valid link to GitHub
    via the "Failure Link" qTest field.

    Metadata:
        github_failure_url_exp (str): Expected GitHub failure link URL.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('github_failure_for_asc.xml', asc_config_file, asc_global_props)

    failure_message = """
            host = &lt;testinfra.host.Host object at 0x7f61d2c20e10&gt;

            @pytest.mark.test_id(&apos;a1f7110e-9bf8-11e8-877e-0025227c8120&apos;)
            @pytest.mark.jira(&apos;JIRA-123&apos;)
            def test_first_stuff(host):
                &quot;&quot;&quot;
                First test
                &quot;&quot;&quot;

        &gt;       assert &quot;FAIL_FIRST_STUFF&quot; not in os.environ
        E       AssertionError: assert &apos;FAIL_FIRST_STUFF&apos; not in {&apos;FAIL_FIRST_STUFF&apos;: &apos;cats&apos;, &apos;ANSIBLE_CONFIG&apos;: &apos;/tmp/molecule/asc-test-repo/default/ansible.cfg&apos;, &apos;MOLECULE_LINT_NAME&apos;...0;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:&apos;, &apos;OS_AUTH_URL&apos;: &apos;https://204.232.230.122:5000/v3&apos;}
        E        +  where {&apos;FAIL_FIRST_STUFF&apos;: &apos;cats&apos;, &apos;ANSIBLE_CONFIG&apos;: &apos;/tmp/molecule/asc-test-repo/default/ansible.cfg&apos;, &apos;MOLECULE_LINT_NAME&apos;...0;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:&apos;, &apos;OS_AUTH_URL&apos;: &apos;https://204.232.230.122:5000/v3&apos;} = os.environ

        tests/test_stuff.py:14: AssertionError"""  # noqa

    # Setup global props and test case for use with the 'https://github.com/rcbops/asc-test-repo/tree/asc' fixture.
    zz_runner.global_props['MOLECULE_TEST_REPO'] = 'asc-test-repo'
    zz_runner.global_props['MOLECULE_SCENARIO_NAME'] = 'default'
    zz_runner.global_props['MOLECULE_GIT_COMMIT'] = 'asc'
    zz_runner.add_test_case(state='failure',
                            name='test_first_stuff',
                            file_path='tests/test_stuff.py',
                            class_name='tests.test_stuff',
                            line=6,
                            message=failure_message)

    # Store the expected GitHub failure link URL to the runner as metadata.
    zz_runner.metadata['github_failure_url_exp'] = ('https://github.com/rcbops/asc-test-repo/tree/asc/molecule/'
                                                    'default/tests/test_stuff.py#L14')

    return zz_runner


@pytest.fixture(scope='session')
def github_failure_for_mk8s(_zigzag_runner_factory, mk8s_config_file, mk8s_global_props):
    """ZigZag CLI runner with a failing test configured for the "mk8s" CI environment to create a valid link to GitHub
    via the "Failure Link" qTest field.

    Metadata:
        github_failure_url_exp (str): Expected GitHub failure link URL.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('github_failure_for_mk8s.xml', mk8s_config_file, mk8s_global_props)

    failure_message = """
            host = &lt;testinfra.host.Host object at 0x7f61d2c20e10&gt;

            @pytest.mark.test_id(&apos;a1f75204-9bf8-11e8-877e-0025227c8120&apos;)
            @pytest.mark.jira(&apos;JIRA-123&apos;)
            def test_first_thing(host):
                &quot;&quot;&quot;
                First test
                &quot;&quot;&quot;

        &gt;       assert &quot;FAIL_FIRST_THING&quot; not in os.environ
        E       AssertionError: assert &apos;FAIL_FIRST_THING&apos; not in {&apos;FAIL_FIRST_THING&apos;: &apos;cats&apos;}
        E        +  where {&apos;FAIL_FIRST_THING&apos;: &apos;cats&apos;} = os.environ

        tests/test-cases/test_things.py:15: AssertionError"""  # noqa

    # Setup global props and test case for use with the 'https://github.com/rcbops/asc-test-repo/tree/mk8s' fixture.
    zz_runner.global_props['GIT_URL'] = 'https://github.com/rcbops/asc-test-repo.git'
    zz_runner.global_props['GIT_COMMIT'] = 'b8627fda1fef02dea802f7eec0fcae9edc700993'
    zz_runner.global_props['CHANGE_BRANCH'] = 'Unknown'
    zz_runner.global_props['CHANGE_FORK'] = 'foo'
    zz_runner.add_test_case(state='failure',
                            name='test_first_thing',
                            file_path='tests/test-cases/test_things.py',
                            class_name='tests.test-cases.test_things.TestSuiteForThings',
                            line=6,
                            message=failure_message)

    # Store the expected GitHub failure link URL to the runner as metadata.
    zz_runner.metadata['github_failure_url_exp'] = ('https://github.com/foo/mk8s/tree/b8627fda1fef02dea802f7eec0fcae9edc700993/'  # noqa
                                                    'tools/installer/tests/test-cases/test_things.py#L15')

    return zz_runner


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
# noinspection PyUnresolvedReferences
class TestGitHubLinking(object):
    """Test cases for validating that assets in qTest can be linked to GitHub."""

    # noinspection PyShadowingNames
    def test_github_link_for_asc(self, github_failure_for_asc):
        """Verify that GitHub failure links are generated correctly using the "asc" CI environment."""

        # Setup
        github_failure_for_asc.assert_invoke_zigzag()
        test_runs = github_failure_for_asc.tests[0].qtest_test_runs

        # Expectations
        github_failure_url_exp = github_failure_for_asc.metadata['github_failure_url_exp']

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Link', github_failure_url_exp)

    # noinspection PyShadowingNames
    def test_missing_github_link_for_asc(self, single_failing_test_for_asc):
        """Verify that GitHub failure links are omitted when required environment variables are absent for the
        "asc" CI environment.
        We will remove the value associated with the config test_commit
        """

        # Setup
        single_failing_test_for_asc.global_props.pop('MOLECULE_GIT_COMMIT')
        single_failing_test_for_asc.assert_invoke_zigzag()
        test_runs = single_failing_test_for_asc.tests[0].qtest_test_runs

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Link', SWEET_UNICORN_GIF)

    # noinspection PyShadowingNames
    def test_github_link_for_mk8s(self, github_failure_for_mk8s):
        """Verify that GitHub failure links are generated correctly using the "mk8s" CI environment."""

        # Setup
        github_failure_for_mk8s.assert_invoke_zigzag()
        test_runs = github_failure_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        github_failure_url_exp = github_failure_for_mk8s.metadata['github_failure_url_exp']

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Link', github_failure_url_exp)

    # noinspection PyShadowingNames
    def test_missing_github_link_for_mk8s(self, single_failing_test_for_mk8s):
        """Verify that GitHub failure links are omitted when required environment variables are absent for the
        "mk8s" CI environment.
        """

        # Setup
        single_failing_test_for_mk8s.global_props.pop('GIT_COMMIT')
        single_failing_test_for_mk8s.assert_invoke_zigzag()
        test_runs = single_failing_test_for_mk8s.tests[0].qtest_test_runs

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Link', SWEET_UNICORN_GIF)
