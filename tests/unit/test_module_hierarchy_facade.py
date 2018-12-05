# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from zigzag.utility_facade import UtilityFacade
from zigzag.module_hierarchy_facade import ModuleHierarchyFacade

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

    def test_asc(self, mocker):
        """Validate when configured with asc as ci-environment"""

        # Mock
        zz = mocker.MagicMock()
        zz.ci_environment = 'asc'
        zz.utility_facade = UtilityFacade(zz)
        zz.testsuite_props = ASC_TESTSUITE_PROPS

        # Setup
        classname = 'tests.test_default'

        # Test
        mhf = ModuleHierarchyFacade(classname, zz)
        mh = mhf.get_module_hierarchy()
        assert mh == ['foo', 'bar', 'baz', 'barf', 'test_default']

    def test_mk8s_pr(self, mocker):
        """Validate when configured with mk8s as ci-environment"""

        # Mock
        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.utility_facade = UtilityFacade(zz)
        zz.testsuite_props = {
            'BRANCH_NAME': 'asc-123/master/stuff',
            'GIT_BRANCH': 'PR-123'
        }

        # Setup
        classname = 'tests.test_default'

        # Test
        mhf = ModuleHierarchyFacade(classname, zz)
        assert mhf.get_module_hierarchy() == ['PR-123', 'tests.test_default']

    def test_mk8s_branch_periodic(self, mocker):
        """Validate when configured with mk8s as ci-environment"""

        # Mock
        zz = mocker.MagicMock()
        zz.ci_environment = 'mk8s'
        zz.utility_facade = UtilityFacade(zz)
        zz.testsuite_props = {
            'BRANCH_NAME': 'master',
            'GIT_BRANCH': 'master'
        }

        # Setup
        classname = 'tests.test_default'

        # Test
        mhf = ModuleHierarchyFacade(classname, zz)
        assert mhf.get_module_hierarchy() == ['tests.test_default']

    def test_tempest(self, mocker):
        """Validate when configured with tempest as tool"""

        # Mock
        zz = mocker.MagicMock()
        zz.test_runner = 'tempest'
        zz.utility_facade = UtilityFacade(zz)

        # Setup
        classname = 'tests.test_default'

        # Test
        mhf = ModuleHierarchyFacade(classname, zz)
        assert mhf.get_module_hierarchy() == ['Tempest']

    def test_bad_value(self, mocker):
        """Validate that if a bad value gets in we default to asc"""
        # Mock
        zz = mocker.MagicMock()
        zz.ci_environment = 'oops'
        zz.utility_facade = UtilityFacade(zz)
        zz.testsuite_props = ASC_TESTSUITE_PROPS

        # Setup
        classname = 'tests.test_default'

        # Test
        mhf = ModuleHierarchyFacade(classname, zz)
        mh = mhf.get_module_hierarchy()
        assert mh == ['foo', 'bar', 'baz', 'barf', 'test_default']
