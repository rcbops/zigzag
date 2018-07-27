# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from zigzag.link_generation_facade import LinkGenerationFacade

LINE_NUMBER = '42'

FAILURE_OUTPUT = """
    @pytest.mark.test_id('d7fc646b-432a-11e8-b858-6a00035510c0')
    @pytest.mark.jira('asc-239')
    def test_verify_network_list(host):
        \"\"\"Verify the neutron network was created\"\"\"
        cmd = pre_cmd + "openstack network list\""
        output = host.run(cmd)
&gt;       assert ("GATEWAY_NET" in output.stdout)
E       assert 'GATEWAY_NET' in ''
E        +  where '' = CommandResult(command='bash -c "source /root/openrc; openstack network list"', exit_status=0, stdout=u'', stderr=u'').stdout

tests/test_verify_networks_created.py:{}: AssertionError
""".format(LINE_NUMBER)  # noqa

TEST_FILE = 'tests/totally_real/verify_I_am_good_link.py'


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestLinkGenerationFacade(object):
    """Tests for the LinkGenerationFacade"""

    def test_asc_failure_link(self, mocker):
        """Validate when configured with asc as ci-environment"""
        re_job_branch = 'pike-rc'
        molecule_test_repo = 'molecule-validate-neutron-deploy'
        molecule_scenario_name = 'default'

        zz = mocker.MagicMock()
        zz.ci_environment = 'asc'
        zz.testsuite_props = {
            'REPO_URL': 'https://github.com/rcbops/rpc-openstack',
            'RE_JOB_BRANCH': re_job_branch,
            'MOLECULE_TEST_REPO': molecule_test_repo,
            'MOLECULE_SCENARIO_NAME': molecule_scenario_name,
        }

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = FAILURE_OUTPUT

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == ('https://github.com/'
                                'rcbops/'
                                '{}/'
                                'blob/{}/'
                                'molecule/{}/'
                                '{}#L{}'.format(molecule_test_repo,
                                                re_job_branch,
                                                molecule_scenario_name,
                                                TEST_FILE,
                                                LINE_NUMBER))

    def test_asc_def_link(self, mocker):
        """Validate fallback to def line number"""
        molecule_test_repo = 'molecule-validate-neutron-deploy'
        re_job_branch = 'pike-rc'
        molecule_scenario_name = 'default'
        def_line_num = '88'

        zz = mocker.MagicMock()
        zz.ci_environment = 'asc'
        zz.testsuite_props = {
            'REPO_URL': 'https://github.com/rcbops/rpc-openstack',
            'RE_JOB_BRANCH': re_job_branch,
            'MOLECULE_TEST_REPO': molecule_test_repo,
            'MOLECULE_SCENARIO_NAME': molecule_scenario_name,
        }

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = 'I dont contain an assert message'
        zztl.def_line_number = '88'

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == ('https://github.com/'
                                'rcbops/'
                                '{}/'
                                'blob/{}/'
                                'molecule/{}/'
                                '{}#L{}'.format(molecule_test_repo,
                                                re_job_branch,
                                                molecule_scenario_name,
                                                TEST_FILE,
                                                def_line_num))

    def test_asc_file_link(self, mocker):
        """Validate fallback to file with no line number"""
        re_job_branch = 'pike-rc'
        molecule_test_repo = 'molecule-validate-neutron-deploy'
        molecule_scenario_name = 'default'

        zz = mocker.MagicMock()
        zz.ci_environment = 'asc'
        zz.testsuite_props = {
            'REPO_URL': 'https://github.com/rcbops/rpc-openstack',
            'RE_JOB_BRANCH': re_job_branch,
            'MOLECULE_TEST_REPO': molecule_test_repo,
            'MOLECULE_SCENARIO_NAME': molecule_scenario_name,
        }

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = 'I dont contain an assert message'
        zztl.def_line_number = ''

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == ('https://github.com/'
                                'rcbops/'
                                '{}/'
                                'blob/{}/'
                                'molecule/{}/'
                                '{}'.format(molecule_test_repo,
                                            re_job_branch,
                                            molecule_scenario_name,
                                            TEST_FILE))

    def test_mk8s_master_branch(self, mocker):
        """Validate when configured with mk8s as ci-environment"""
        git_branch = 'master'

        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.testsuite_props = {
            'GIT_URL': 'https://github.com/rcbops/mk8s.git',
            'GIT_BRANCH': git_branch,
        }

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = FAILURE_OUTPUT

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == ('https://github.com/'
                                'rcbops/'
                                'mk8s/'
                                'blob/{}/'
                                'tools/installer/'
                                '{}#L{}'.format(git_branch,
                                                TEST_FILE,
                                                LINE_NUMBER))

    def test_mk8s_missing_data(self, mocker):
        """Failure link should be 'Unknown' when it cant be calculated"""
        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.testsuite_props = {}

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = FAILURE_OUTPUT

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == 'Unknown'

    def test_asc_missing_data(self, mocker):
        """Failure link should be 'Unknown' when it cant be calculated"""
        zz = mocker.MagicMock()
        zz.ci_environment = 'asc'
        zz.testsuite_props = {}

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = FAILURE_OUTPUT

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == 'Unknown'

    def test_mk8s_pr_testing(self, mocker):
        """Validate when configured with mk8s as ci-environment testing a PR"""
        git_branch = 'master'
        change_branch = 'asc-123/master/this_is_my_feature'
        change_fork = 'zreichert'

        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.testsuite_props = {
            'GIT_URL': 'https://github.com/rcbops/mk8s.git',
            'GIT_BRANCH': git_branch,
            'CHANGE_BRANCH': change_branch,
            'CHANGE_FORK': change_fork,
        }

        zztl = mocker.MagicMock()
        zztl.test_file = TEST_FILE
        zztl.failure_output = FAILURE_OUTPUT

        lgf = LinkGenerationFacade(zz)
        failure_link = lgf.github_testlog_failure_link(zztl)
        assert failure_link == ('https://github.com/'
                                '{}/'
                                'mk8s/'
                                'blob/{}/'
                                'tools/installer/'
                                '{}#L{}'.format(change_fork,
                                                change_branch,
                                                TEST_FILE,
                                                LINE_NUMBER))
