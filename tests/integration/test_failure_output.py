# -*- coding: utf-8 -*-

"""Tests for verifying failure output."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest


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
    def test_failure_output_after_state_change_for_asc(self, single_failing_test_for_asc):
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

        # Setup
        single_failing_test_for_asc.tests[0].state = 'passed'   # Change the state of the test to 'passed'
        single_failing_test_for_asc.assert_invoke_zigzag(force_clean_up=False)     # Re-run ZigZag
        test_runs = single_failing_test_for_asc.tests[0].qtest_test_runs

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Output', '')

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
    def test_failure_output_after_state_change_for_mk8s(self, single_failing_test_for_mk8s):
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

        # Setup
        single_failing_test_for_mk8s.tests[0].state = 'passed'  # Change the state of the test to 'passed'
        single_failing_test_for_mk8s.assert_invoke_zigzag(force_clean_up=False)  # Re-run ZigZag
        test_runs = single_failing_test_for_mk8s.tests[0].qtest_test_runs

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property(test_runs[0], 'Failure Output', '')

    # noinspection PyUnresolvedReferences
    def test_truncated_failure_output_for_asc(self, multi_line_failure_message_for_asc):
        """Verify the qTest 'Failure Output' test log field is populated with the correct message for a single test
        failing from the "asc" CI environment.
        """

        # Setup
        multi_line_failure_message_for_asc.assert_invoke_zigzag()
        test_runs = multi_line_failure_message_for_asc.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_regex_exp = r"E       assert 'Ubuntu 14\.04 LTS' in ''"

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)

    # noinspection PyUnresolvedReferences
    def test_truncated_failure_output_for_mk8s(self, multi_line_failure_message_for_mk8s):
        """Verify the qTest 'Failure Output' test log field is populated with the correct message for a single test
        failing from the "asc" CI environment.
        """

        # Setup
        multi_line_failure_message_for_mk8s.assert_invoke_zigzag()
        test_runs = multi_line_failure_message_for_mk8s.tests[0].qtest_test_runs

        # Expectations
        test_failure_msg_regex_exp = r"E       docker\.errors\.APIError: 500 Server Error"

        # Test
        assert len(test_runs) == 1
        pytest.helpers.assert_qtest_property_search(test_runs[0], 'Failure Output', test_failure_msg_regex_exp)
