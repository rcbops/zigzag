# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from zigzag.link_generation_facade import LinkGenerationFacade
from zigzag.zigzag_config import ZigZagConfig
import pytest

LINE_NUMBER = '42'
SHA = '36d8d764f9bac665b21837259247bd4cbaf0c674'
TEST_FILE = 'totally_real/verify_I_am_good_link.py'

# This failure output contains two different line numbers
# We want the first one
FAILURE_OUTPUT = """
k8sclient = <tests.kubernetes.deploy.K8sClient object at 0x7f48f8c0a7f0>
persistent_volume_claim = <function persistent_volume_claim at 0x7f48f8c00158>
deployment = <function deployment at 0x7f48f91482f0>

@pytest.mark.test_id('d8e153fc-74d7-11e8-b0cf-0025227c8120')
@pytest.mark.jira('K8S-838')
def test_cinder_integration_same_node(
k8sclient, persistent_volume_claim, deployment):
log.info("test cinder integration pod rescheduled on same node")
testname = "test-cinder-integration-same-node"
# verify pod is running and attached to the persistent volume successfully
> podname = pod(k8sclient, testname)

{}:{}: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

k8sclient = <tests.kubernetes.deploy.K8sClient object at 0x7f48f8c0a7f0>
testname = 'test-cinder-integration-same-node'

def pod(k8sclient, testname):
# get the pod corresponding to the given deployment
podlist = k8sclient.get_pod_list(
namespace=KubeConstants.NAMESPACE,
for pod in podlist.items:
if (testname in pod.metadata.name) \
and (pod.status.phase == KubeStatus.STATUS_PENDING):
podname = pod.metadata.name
log.info("Pod name is %s" % podname)

# Wait for the pod to be ready
status = ""
end_time = time.time() + KubeConstants.TIMEOUT
while status != KubeStatus.STATUS_RUNNING and time.time() <= end_time:
response = k8sclient.read_pod_status(
name=podname,
namespace=KubeConstants.NAMESPACE)
log.info(response.status.phase)
if response.status.phase == KubeStatus.STATUS_RUNNING:
log.info("Pod created successfully")
status = KubeStatus.STATUS_RUNNING
else:
time.sleep(KubeConstants.WAIT_INTERVAL)
continue
> assert status == KubeStatus.STATUS_RUNNING
E AssertionError: assert '' == 'Running'
E + Running

tests/test-cases/test-k8s/test_cinder_integration.py:94: AssertionError
""".format(TEST_FILE, LINE_NUMBER)  # noqa


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestLinkGenerationFacade(object):
    """Tests for the LinkGenerationFacade"""

    def test_asc_failure_link(self, asc_zigzag_config_file, mocker):
        """Validate when configured with asc as ci-environment"""

        molecule_test_repo = 'molecule-validate-neutron-deploy'
        molecule_scenario_name = 'default'
        testsuite_props = {
            'REPO_URL': 'https://github.com/rcbops/rpc-openstack',
            'MOLECULE_GIT_COMMIT': SHA,
            'MOLECULE_TEST_REPO': molecule_test_repo,
            'MOLECULE_SCENARIO_NAME': molecule_scenario_name,
        }

        # mock
        zz = mocker.MagicMock()
        zztl = mocker.MagicMock()
        zztl._mediator = zz

        zztl.test_file = TEST_FILE
        zztl.failure_output = 'This property contains truncated content......'
        zztl.full_failure_output = FAILURE_OUTPUT

        zz.config_dict = ZigZagConfig(asc_zigzag_config_file, testsuite_props)

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == ('https://github.com/'
                                'rcbops/'
                                '{}/'
                                'tree/{}/'
                                'molecule/{}/tests/'
                                '{}#L{}'.format(molecule_test_repo,
                                                SHA,
                                                molecule_scenario_name,
                                                TEST_FILE,
                                                LINE_NUMBER))

    def test_asc_def_link(self, asc_zigzag_config_file, mocker):
        """Validate fallback to def line number"""

        molecule_test_repo = 'molecule-validate-neutron-deploy'
        molecule_scenario_name = 'default'
        def_line_num = '88'
        testsuite_props = {
            'REPO_URL': 'https://github.com/rcbops/rpc-openstack',
            'MOLECULE_GIT_COMMIT': SHA,
            'MOLECULE_TEST_REPO': molecule_test_repo,
            'MOLECULE_SCENARIO_NAME': molecule_scenario_name,
        }

        # Mock
        zz = mocker.MagicMock()
        zztl = mocker.MagicMock()

        zztl.test_file = TEST_FILE
        zztl.failure_output = 'This property contains truncated content......'
        zztl.full_failure_output = 'I dont contain an assert message'
        zztl.def_line_number = def_line_num

        zz.config_dict = ZigZagConfig(asc_zigzag_config_file, testsuite_props)

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == ('https://github.com/'
                                'rcbops/'
                                '{}/'
                                'tree/{}/'
                                'molecule/{}/tests/'
                                '{}#L{}'.format(molecule_test_repo,
                                                SHA,
                                                molecule_scenario_name,
                                                TEST_FILE,
                                                def_line_num))

    def test_asc_file_link(self, asc_zigzag_config_file, mocker):
        """Validate fallback to file with no line number"""

        molecule_test_repo = 'molecule-validate-neutron-deploy'
        molecule_scenario_name = 'default'
        testsuite_props = {
            'REPO_URL': 'https://github.com/rcbops/rpc-openstack',
            'MOLECULE_GIT_COMMIT': SHA,
            'MOLECULE_TEST_REPO': molecule_test_repo,
            'MOLECULE_SCENARIO_NAME': molecule_scenario_name,
        }

        # Mock
        zz = mocker.MagicMock()
        zztl = mocker.MagicMock()

        zztl.test_file = TEST_FILE
        zztl.failure_output = 'This property contains truncated content......'
        zztl.full_failure_output = 'I dont contain an assert message'
        zztl.def_line_number = ''

        zz.config_dict = ZigZagConfig(asc_zigzag_config_file, testsuite_props)

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == ('https://github.com/'
                                'rcbops/'
                                '{}/'
                                'tree/{}/'
                                'molecule/{}/tests/'
                                '{}'.format(molecule_test_repo,
                                            SHA,
                                            molecule_scenario_name,
                                            TEST_FILE))

    def test_mk8s_master_branch(self, mk8s_zigzag_config_file, mocker):
        """Validate when configured with mk8s as ci-environment"""

        zz = mocker.MagicMock()
        testsuite_props = {
            'GIT_URL': 'https://github.com/rcbops/mk8s.git',
            'GIT_COMMIT': SHA,
        }

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = 'This property contains truncated content......'
        zztl.full_failure_output = FAILURE_OUTPUT

        zz.config_dict = ZigZagConfig(mk8s_zigzag_config_file, testsuite_props)

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == ('https://github.com/'
                                'rcbops/'
                                'mk8s/'
                                'tree/{}/'
                                'tools/installer/tests/'
                                '{}#L{}'.format(SHA,
                                                TEST_FILE,
                                                LINE_NUMBER))

    def test_mk8s_missing_data(self, mk8s_zigzag_config_file, mocker):
        """Failure link should be None when it cant be calculated"""
        zz = mocker.MagicMock()
        testsuite_props = {}

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = 'This property contains truncated content......'
        zztl.full_failure_output = FAILURE_OUTPUT

        zz.config_dict = ZigZagConfig(mk8s_zigzag_config_file, testsuite_props)

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link is None

    def test_asc_missing_data(self, asc_zigzag_config_file, mocker):
        """Failure link should be None when it cant be calculated"""
        zz = mocker.MagicMock()

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = 'This property contains truncated content......'
        zztl.full_failure_output = FAILURE_OUTPUT

        zz.config_dict = ZigZagConfig(asc_zigzag_config_file, {})

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link is None

    def test_mk8s_pr_testing(self, mk8s_zigzag_config_file, mocker):
        """Validate when configured with mk8s as ci-environment testing a PR"""
        change_branch = 'asc-123/master/this_is_my_feature'
        change_fork = 'zreichert'

        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        testsuite_props = {
            'GIT_URL': 'https://github.com/rcbops/mk8s.git',
            'GIT_COMMIT': SHA,
            'CHANGE_BRANCH': change_branch,
            'CHANGE_FORK': change_fork,
        }

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = 'This property contains truncated content......'
        zztl.full_failure_output = FAILURE_OUTPUT

        zz.config_dict = ZigZagConfig(mk8s_zigzag_config_file, testsuite_props)

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == ('https://github.com/'
                                '{}/'
                                'mk8s/'
                                'tree/{}/'
                                'tools/installer/tests/'
                                '{}#L{}'.format(change_fork,
                                                SHA,
                                                TEST_FILE,
                                                LINE_NUMBER))

    @pytest.mark.skip(reason="This method is not used in production, perhaps should be eliminated")
    def test_asc_diff_link(self, mocker):
        """Validate when configured with asc as ci-environment"""
        molecule_test_repo = 'molecule-validate-neutron-deploy'
        molecule_scenario_name = 'default'
        fork = 'rcbops'

        zz = mocker.MagicMock()
        zz.ci_environment = 'asc'
        zz.testsuite_props = {
            'REPO_URL': 'https://github.com/{}/rpc-openstack'.format(fork),
            'MOLECULE_GIT_COMMIT': SHA,
            'MOLECULE_TEST_REPO': molecule_test_repo,
            'MOLECULE_SCENARIO_NAME': molecule_scenario_name,
        }

        lgf = LinkGenerationFacade(zz)
        pass_fork = 'zreichert'
        pass_base = 'master'

        diff_link = lgf.github_diff_link(pass_fork, pass_base)
        assert diff_link == ('https://github.com/'
                             '{}/'
                             '{}/'
                             'compare/'
                             '{}...{}:{}'.format(fork,
                                                 molecule_test_repo,
                                                 SHA,
                                                 pass_fork,
                                                 pass_base))

    @pytest.mark.skip(reason="This method is not used in production, perhaps should be eliminated")
    def test_mk8s_diff_link(self, mocker):
        """Validate when configured with mk8s as ci-environment"""
        fork = 'rcbops'
        repo_name = 'mk8s'

        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.testsuite_props = {
            'GIT_URL': 'https://github.com/{}/{}.git'.format(fork, repo_name),
            'GIT_COMMIT': SHA,
        }

        lgf = LinkGenerationFacade(zz)
        pass_fork = 'zreichert'
        pass_base = 'master'

        diff_link = lgf.github_diff_link(pass_fork, pass_base)
        assert diff_link == ('https://github.com/'
                             '{}/'
                             '{}/'
                             'compare/'
                             '{}...{}:{}'.format(fork,
                                                 repo_name,
                                                 SHA,
                                                 pass_fork,
                                                 pass_base))

    def test_mk8s_diff_link_missing_info(self, mocker):
        """diff link should be 'Unknown' when it cant be calculated"""

        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.testsuite_props = {}

        lgf = LinkGenerationFacade(zz)
        pass_fork = 'zreichert'
        pass_base = 'master'

        diff_link = lgf.github_diff_link(pass_fork, pass_base)
        assert diff_link == 'Unknown'

    def test_asc_diff_link_missing_info(self, mocker):
        """diff link should be 'Unknown' when it cant be calculated"""

        zz = mocker.MagicMock()
        zz.ci_environment = 'asc'
        zz.testsuite_props = {}

        lgf = LinkGenerationFacade(zz)
        pass_fork = 'zreichert'
        pass_base = 'master'

        diff_link = lgf.github_diff_link(pass_fork, pass_base)
        assert diff_link == 'Unknown'
