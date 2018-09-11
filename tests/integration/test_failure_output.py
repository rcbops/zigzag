# -*- coding: utf-8 -*-

"""Tests for verifying failure output."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
from zigzag.zigzag_test_log import SWEET_UNICORN_GIF


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
# noinspection PyShadowingNames
@pytest.fixture
def multi_line_failure_message_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with one failing test that has a multi-line failure
    message which will need to be truncated.

    Returns:
        ZigZagRunner
    """

    failure_message = '''host = &lt;testinfra.host.Host object at 0x7fa5a7fda3d0&gt;

    @pytest.mark.test_id('d7fc612b-432a-11e8-9a7a-6a00035510c0')
    @pytest.mark.jira('asc-240')
    def test_verify_glance_image(host):
        """Verify the glance images created by:
        https://github.com/openstack/openstack-ansible-ops/blob/master/multi-node-aio/playbooks/vars/openstack-service-config.yml
        """
        cmd = attach_utility_container + "'. /root/openrc ; openstack image list'"
        output = host.run(cmd)
&gt;       assert ("Ubuntu 14.04 LTS" in output.stdout)
E       assert 'Ubuntu 14.04 LTS' in ''
E        +  where '' = CommandResult(command="lxc-attach -n `lxc-ls -1 | grep utility | head -n 1` --...ls is deprecated and will be removed after Jun 2017. Please use osc_lib.utils').stdout

tests/test_scan_images_and_flavors.py:26: AssertionError'''     # noqa

    zz_runner = _zigzag_runner_factory('multi_line_failure_message_for_asc.xml', 'asc')
    zz_runner.add_test_case('failure', message=failure_message)

    return zz_runner


# noinspection PyShadowingNames
@pytest.fixture
def multi_line_failure_message_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner configured for the "asc" CI environment with one failing test that has a multi-line failure
    message which will need to be truncated.

    Returns:
        ZigZagRunner
    """

    failure_message = '''self = &lt;docker.api.client.APIClient object at 0x7f3047082080&gt;
response = &lt;Response [500]&gt;

    def _raise_for_status(self, response):
        """Raises stored :class:`APIError`, if one occurred."""
        try:
&gt;           response.raise_for_status()

/usr/local/lib/python3.5/dist-packages/docker/api/client.py:225: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = &lt;Response [500]&gt;

    def raise_for_status(self):
        """Raises stored :class:`HTTPError`, if one occurred."""

        http_error_msg = ''
        if isinstance(self.reason, bytes):
            # We attempt to decode utf-8 first because some servers
            # choose to localize their reason strings. If the string
            # isn't utf-8, we fall back to iso-8859-1 for all other
            # encodings. (See PR #3538)
            try:
                reason = self.reason.decode('utf-8')
            except UnicodeDecodeError:
                reason = self.reason.decode('iso-8859-1')
        else:
            reason = self.reason

        if 400 &lt;= self.status_code &lt; 500:
            http_error_msg = u'%s Client Error: %s for url: %s' % (self.status_code, reason, self.url)

        elif 500 &lt;= self.status_code &lt; 600:
            http_error_msg = u'%s Server Error: %s for url: %s' % (self.status_code, reason, self.url)

        if http_error_msg:
&gt;           raise HTTPError(http_error_msg, response=self)
E           requests.exceptions.HTTPError: 500 Server Error: Internal Server Error for url: http+docker://localhost/v1.35/auth

/usr/local/lib/python3.5/dist-packages/requests/models.py:935: HTTPError

During handling of the above exception, another exception occurred:

authtoken = 'c04b8a551535c99f2743d24a4237f46d9b9ac566c2d63906f8b06fd3a557ddc0'
harbor_project = 'mk8s-t-inst-pr-261-27'

    @pytest.mark.test_id('14d8e10a-7568-11e8-ab5e-0025227c8120')
    @pytest.mark.jira('K8S-877')
    @pytest.mark.parametrize('harbor_project',
                             [(DockerRegistry.OS_USERNAME, 'authtoken')],
                             indirect=True)
    def test_nonadmin_push_and_delete(authtoken, harbor_project):
        """
         push/pull from docker registry while logging in as user

        """
        # login as user and create a project
        user_registry = "{registry}/{project_name}/{image_name}". \
            format(registry=DockerRegistry.REGISTRY,
                   project_name=harbor_project,
                   image_name=DockerRegistry.IMAGE)

        # CLI login to registry as user using token
        response = client.login(username=DockerRegistry.OS_USERNAME,
                                password=authtoken,
&gt;                               registry=user_registry)

tests/quality_check/managedservices/test_harbor.py:66: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.5/dist-packages/docker/api/daemon.py:150: in login
    return self._result(response, json=True)
/usr/local/lib/python3.5/dist-packages/docker/api/client.py:231: in _result
    self._raise_for_status(response)
/usr/local/lib/python3.5/dist-packages/docker/api/client.py:227: in _raise_for_status
    raise create_api_error_from_http_exception(e)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

e = HTTPError('500 Server Error: Internal Server Error for url: http+docker://localhost/v1.35/auth',)

    def create_api_error_from_http_exception(e):
        """
        Create a suitable APIError from requests.exceptions.HTTPError.
        """
        response = e.response
        try:
            explanation = response.json()['message']
        except ValueError:
            explanation = (response.content or '').strip()
        cls = APIError
        if response.status_code == 404:
            if explanation and ('No such image' in str(explanation) or
                                'not found: does not exist or no pull access'
                                in str(explanation) or
                                'repository does not exist' in str(explanation)):
                cls = ImageNotFound
            else:
                cls = NotFound
&gt;       raise cls(e, response=response, explanation=explanation)
E       docker.errors.APIError: 500 Server Error: Internal Server Error ("Get https://registry.kubernetes-mk8s-t-inst-pr-261-27.mk8s-t-inst-pr-261-27.mk8s.systems/v2/: net/http: request canceled (Client.Timeout exceeded while awaiting headers)")

/usr/local/lib/python3.5/dist-packages/docker/errors.py:31: APIError'''     # noqa

    zz_runner = _zigzag_runner_factory('multi_line_failure_message_for_mk8s.xml', 'mk8s')
    zz_runner.add_test_case('failure', message=failure_message)

    return zz_runner


@pytest.fixture(scope='session')
def state_change_failure_for_asc(_zigzag_runner_factory):
    """ZigZag CLI runner with a failing test configured for the "asc" CI environment to create a valid link to GitHub
    via the "Failure Link" qTest field.

    Metadata:
        github_failure_url_exp (str): Expected GitHub failure link URL.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('github_failure_for_asc.xml', 'asc')

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
                            name='test_state_change_asc',
                            file_path='tests/test_state_change_asc.py',
                            class_name='tests.test_state_change_asc',
                            line=6,
                            message=failure_message)

    # Store the expected GitHub failure link URL to the runner as metadata.
    zz_runner.metadata['github_failure_url_exp'] = ('https://github.com/rcbops/asc-test-repo/tree/asc/molecule/'
                                                    'default/tests/test_stuff.py#L14')

    return zz_runner


@pytest.fixture(scope='session')
def state_change_failure_for_mk8s(_zigzag_runner_factory):
    """ZigZag CLI runner with a failing test configured for the "mk8s" CI environment to create a valid link to GitHub
    via the "Failure Link" qTest field.

    Metadata:
        github_failure_url_exp (str): Expected GitHub failure link URL.

    Returns:
        ZigZagRunner
    """

    zz_runner = _zigzag_runner_factory('github_failure_for_mk8s.xml', 'mk8s')

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
    zz_runner.global_props['GIT_COMMIT'] = 'mk8s'
    zz_runner.global_props['CHANGE_BRANCH'] = 'Unknown'
    zz_runner.add_test_case(state='failure',
                            name='test_state_change_mk8s',
                            file_path='tests/test-cases/test_state_change_mk8s.py',
                            class_name='tests.test-cases.test_state_change_mk8s.TestSuiteForThings',
                            line=6,
                            message=failure_message)

    # Store the expected GitHub failure link URL to the runner as metadata.
    zz_runner.metadata['github_failure_url_exp'] = ('https://github.com/rcbops/asc-test-repo/tree/mk8s/'
                                                    'tools/installer/tests/test-cases/test_things.py#L15')

    return zz_runner


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestFailureOutputField(object):
    """Test cases for validating that failing/erroring test cases will have failure messages populated in the qTest
    'Failure Output' test log field.
    """

    # noinspection PyUnresolvedReferences
    def test_failure_output_for_asc(self, single_failing_test_for_asc):
        """Verify the qTest 'Failure Output' test log field is populated with the correct message for a single test
        failing from the "asc" CI environment.
        """

        # Setup
        single_failing_test_for_asc.assert_invoke_zigzag()
        test_runs = single_failing_test_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_regex_exp = r'Test execution state: failure'

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)

    # noinspection PyUnresolvedReferences
    def test_failure_behavior_after_state_change_for_asc(self, state_change_failure_for_asc):
        """Verify the qTest 'Failure Output' and 'Failure Link' test log field is populated with the correct message
        for a single test failing from the "asc" CI environment.
        """

        # Setup
        state_change_failure_for_asc.assert_invoke_zigzag()
        test_runs = state_change_failure_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_regex_exp = r"AssertionError: assert 'FAIL_FIRST_STUFF'"
        test_failure_link_regex_exp = r'http.*'

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Link', test_failure_link_regex_exp)

        # Setup
        state_change_failure_for_asc.tests[0].state = 'passed'   # Change the state of the test to 'passed'
        state_change_failure_for_asc.assert_invoke_zigzag()     # Re-run ZigZag
        test_runs = state_change_failure_for_asc.tests[0].qtest_test_runs

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Output', '')
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Link', SWEET_UNICORN_GIF)

    # noinspection PyUnresolvedReferences
    def test_failure_output_for_mk8s(self, single_failing_test_for_mk8s):
        """Verify the qTest 'Failure Output' test log field is populated with the correct message for a single test
        failing from the "mk8s" CI environment.
        """

        # Setup
        single_failing_test_for_mk8s.assert_invoke_zigzag()
        test_runs = single_failing_test_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_regex_exp = r'Test execution state: failure'

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)

    # noinspection PyUnresolvedReferences
    def test_failure_behavior_after_state_change_for_mk8s(self, state_change_failure_for_mk8s):
        """Verify the qTest 'Failure Output' and 'Failure Link' test log field is populated with the correct message
        for a single test failing from the "mk8s" CI environment.
        """

        # Setup
        state_change_failure_for_mk8s.assert_invoke_zigzag()
        test_runs = state_change_failure_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_regex_exp = r"AssertionError: assert 'FAIL_FIRST_THING'"
        test_failure_link_regex_exp = r'http.*'

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Link', test_failure_link_regex_exp)

        # Setup
        state_change_failure_for_mk8s.tests[0].state = 'passed'  # Change the state of the test to 'passed'
        state_change_failure_for_mk8s.assert_invoke_zigzag()  # Re-run ZigZag
        test_runs = state_change_failure_for_mk8s.tests[0].qtest_test_runs

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Output', '')
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Link', SWEET_UNICORN_GIF)

    # noinspection PyUnresolvedReferences
    def test_truncated_failure_output_for_asc(self, multi_line_failure_message_for_asc):
        """Verify the qTest 'Failure Output' test log field is populated with the correct message for a single test
        failing from the "asc" CI environment.
        """

        # Setup
        multi_line_failure_message_for_asc.assert_invoke_zigzag()
        test_runs = multi_line_failure_message_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_exp = """Log truncated, please see attached failure log for more details...
E       assert 'Ubuntu 14.04 LTS' in ''
E        +  where '' = CommandResult(command="lxc-attach -n `lxc-ls -1 | grep utility | head -n 1` --...ls is deprecated..."""     # noqa

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Output', test_failure_msg_exp)

    # noinspection PyUnresolvedReferences
    def test_truncated_failure_output_for_mk8s(self, multi_line_failure_message_for_mk8s):
        """Verify the qTest 'Failure Output' test log field is populated with the correct message for a single test
        failing from the "asc" CI environment.
        """

        # Setup
        multi_line_failure_message_for_mk8s.assert_invoke_zigzag()
        test_runs = multi_line_failure_message_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_exp = """Log truncated, please see attached failure log for more details...
>       raise cls(e, response=response, explanation=explanation)
E       docker.errors.APIError: 500 Server Error: Internal Server Error ("Get https://registry.kubernetes-mk8s-t-inst-pr..."""  # noqa

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Output', test_failure_msg_exp)
