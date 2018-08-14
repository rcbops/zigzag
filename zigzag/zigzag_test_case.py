# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================

from __future__ import absolute_import
import re
import json
import ast
import astor
from zigzag.link_generation_facade import LinkGenerationFacade
from zigzag.utility_facade import UtilityFacade


class ZigZagTestCase(object):

    link_generation_facade = 0
    _automation_content_field_id = 0

    def __init__(self, test, branch, file_path, mediator):
        """Create a ZigZagTestCase object

        Args:
            test (ASTNode): A AST Node element representing a testcase.
            mediator (ZigZag): the mediator that stores shared data
        """
        self._mediator = mediator
        self._ast_node = test

        self._git_links = {}
        self._test_steps = []
        self._description = ast.get_docstring(self._ast_node)
        self._test_id = self._get_decorator_values_by_name('test_id')[0]
        self._name = test.name
        end_line = test.lineno + len(astor.to_source(test).split('\n'))

        # TODO hack
        path = file_path[54:]  # need to refactor so we have a relative path in the repo
        self._url = self.link_generation_facade.github_range_link(fork='rcbops',
                                                                  molecule='molecule-validate-cinder-deploy',  # TODO fix me
                                                                  branch=branch,
                                                                  scenario='default',
                                                                  test_file=path,
                                                                  start_line=test.lineno,
                                                                  end_line=end_line)  # TODO remove the leading path

        self._jira_issues = self._get_decorator_values_by_name('jira')
        for node in ast.walk(test):
            if isinstance(node, ast.Assert):
                self._test_steps.append(astor.to_source(node))

    def _get_decorator_values_by_name(self, decorator_name):
        for decorator in self._ast_node.decorator_list:
            if decorator.func.attr == decorator_name:
                return [x.s for x in decorator.args]

    @property
    def test_steps(self):
        return self._test_steps

    @property
    def description(self):
        return self._description

    @property
    def qtest_test_case(self):
        pass  # TODO not sure it this should go here

    @property
    def test_id(self):
        return self._test_id

    @property
    def name(self):
        return self._name

    @property
    def git_link(self):
        return self._url

    @property
    def jira_link(self):
        return self._jira_link

    @property
    def git_links(self):
        return self._git_links

    @git_links.setter
    def git_links(self, value):
        self._git_links = value

    @property
    def link_generation_facade(self):
        """Gets the instance attached to the class of
        LinkGenerationFacade

        Returns:
            LinkGenerationFacade
        """
        return self._get_link_generation_facade(self._mediator)

    @property
    def automation_content_field_id(self):
        """Gets the Automation Content field id

        Returns:
            int: The id of the 'Automation Content' field for test-case objects
        """
        return self._get_automation_content_field_id(self._mediator)

    @classmethod
    def _get_link_generation_facade(cls, mediator):
        """Get The instance of LinkGenerationFacade

        Args:
            mediator (ZigZag): The ZigZag mediator

        Returns:
            LinkGenerationFacade
        """
        return LinkGenerationFacade(mediator)

    @classmethod
    def _get_automation_content_field_id(cls, mediator):
        """Gets the failure_link_field_id from this class

        Args:
            mediator (ZigZag): The ZigZag mediator

        Returns:
            int: The ID for failure_link_field_id
        """
        if cls._automation_content_field_id == 0:
            cls._automation_content_field_id = \
                UtilityFacade(mediator).find_custom_field_id_by_label('Automation Content', 'test-cases')
        return cls._automation_content_field_id

