# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from zigzag.module_hierarchy_facade import ModuleHierarchyFacade
from lxml import etree

ASC_TESTSUITE_PROPS = {
    'RPC_RELEASE': 'foo',
    'JOB_NAME': 'bar',
    'MOLECULE_TEST_REPO': 'baz',
    'MOLECULE_SCENARIO_NAME': 'barf',
    'RPC_PRODUCT_RELEASE': 'queens'
}


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestModuleHierarchyFacade(object):
    """Tests for the ModuleHierarchyFacade"""

    def test_asc(self, single_passing_xml, mocker):
        """Validate when configured with asc as ci-environment"""
        zz = mocker.MagicMock()
        zz.ci_environment = 'asc'
        zz.testsuite_props = ASC_TESTSUITE_PROPS
        junit_xml_doc = etree.parse(single_passing_xml)
        test_case_xml = junit_xml_doc.find('testcase')

        mhf = ModuleHierarchyFacade(test_case_xml, zz)
        mh = mhf.get_module_hierarchy()
        assert mh == ['foo', 'bar', 'baz', 'barf', 'test_default']

    def test_mk8s_pr(self, single_passing_xml, mocker):
        """Validate when configured with mk8s as ci-environment"""
        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.testsuite_props = {
            'BRANCH_NAME': 'asc-123/master/stuff',
            'GIT_BRANCH': 'PR-123'
        }
        junit_xml_doc = etree.parse(single_passing_xml)
        test_case_xml = junit_xml_doc.find('testcase')

        mhf = ModuleHierarchyFacade(test_case_xml, zz)
        assert mhf.get_module_hierarchy() == ['PR-123', 'tests.test_default']

    def test_mk8s_branch_periodic(self, single_passing_xml, mocker):
        """Validate when configured with mk8s as ci-environment"""
        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.testsuite_props = {
            'BRANCH_NAME': 'master',
            'GIT_BRANCH': 'master'
        }
        junit_xml_doc = etree.parse(single_passing_xml)
        test_case_xml = junit_xml_doc.find('testcase')

        mhf = ModuleHierarchyFacade(test_case_xml, zz)
        assert mhf.get_module_hierarchy() == ['tests.test_default']

    def test_bad_value(self, single_passing_xml, mocker):
        """Validate that if a bad value gets in we default to asc"""
        zz = mocker.MagicMock()
        zz.ci_environment = 'ooops'
        zz.testsuite_props = ASC_TESTSUITE_PROPS
        junit_xml_doc = etree.parse(single_passing_xml)
        test_case_xml = junit_xml_doc.find('testcase')

        mhf = ModuleHierarchyFacade(test_case_xml, zz)
        mh = mhf.get_module_hierarchy()
        assert mh == ['foo', 'bar', 'baz', 'barf', 'test_default']
