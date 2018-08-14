# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================

from __future__ import absolute_import
import re
import json


class ZigZagGitSource(object):

    def __init__(self, mediator):
        """Create a ZigZagGitSource object

        Args:
            mediator (ZigZag): the mediator that stores shared data
        """
        self._mediator = mediator
        self._branches = []
        self._origin_url = None

    @property
    def origin_url(self):
        """Gets the url of the origin

        Returns:
            str: The ulr of the origin
        """
        return self._origin_url

    @origin_url.setter
    def origin_url(self, value):
        """Sets the origin_url"""
        self._origin_url = value

    @property
    def branches(self):
        """Gets a list of the known branches

        Returns:
            str: The ulr of the origin
        """
        return self._branches

    @property
    def reduced_tests(self):
        """Gets the list of ZigZagTestCase that exists across all brances
        tests will be updated to include all links to tests on all branches
        """
        #TODO
        # should test-cases be comparable??? yes????
        # I need a way to quickly reduce all the tests across all of the branches, I think I can do that here
        # this is hacky :(
        # this should process the default branch first
        reduced = {}
        for branch in self.branches:
            for test_id, test_case in branch.test_cases.items():
                if test_id not in reduced:
                    reduced[test_id] = test_case
                    reduced[test_id].git_links[branch] = test_case.git_link
                else:
                    reduced[test_id].git_links[branch] = test_case.git_link
        return reduced

    def get_branch(self, branch_name):
        for branch in self.branches:
            if branch.name == branch_name:
                return branch
        return None

    def add_branch(self, branch):
        self.branches.append(branch)
