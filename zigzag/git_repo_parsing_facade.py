# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================

from __future__ import absolute_import
import os
import pytest_rpc


class GitRepoParsingFacade(object):

    def __init__(self, path):
        self._mediator = mediator

    def parse(self):
        """Parse the xml that is attached to the mediator
        All results are attached the mediator passed in on instantiation
        sets the property 'build_url' on the mediator
        sets the property 'build_number' on the mediator
        """
        self._read()
        self._determine_ci_environment()
        self._validate()
        self._mediator.testsuite_props = {
            p.attrib['name']: p.attrib['value'] for p in self._mediator.junit_xml.findall('./properties/property')}
        self._mediator.serialized_junit_xml = etree.tostring(
            self._mediator.junit_xml, encoding='UTF-8', xml_declaration=True)
        try:
            self._mediator.build_url = self._mediator.testsuite_props['BUILD_URL']
            self._mediator.build_number = self._mediator.testsuite_props['BUILD_NUMBER']
        except KeyError as e:
            raise RuntimeError("Test suite is missing the required property!\n\n{}".format(str(e)))
        for testcase_xml in self._mediator.junit_xml.findall('testcase'):
            ZigZagTestLog(testcase_xml, self._mediator)  # new test logs attach themselves to the mediator
