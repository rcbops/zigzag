# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================

from __future__ import absolute_import


class ZigZagGitBranch(object):

    def __init__(self, name, head_sha, test_cases):
        self._name = name
        self._head_sha = head_sha
        self._test_cases = test_cases

    @property
    def head_sha(self):
        return self._head_sha

    @property
    def name(self):
        return self._name

    @property
    def test_cases(self):
        return self._test_cases
