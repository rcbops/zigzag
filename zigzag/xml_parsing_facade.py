# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================

from __future__ import absolute_import
import os
import pytest_rpc
from lxml import etree
from zigzag.test_log import TestLog


class XmlParsingFacade(object):

    _MAX_FILE_SIZE = 52428800

    def __init__(self, mediator):
        """A facade to parse xml
        An XmlParsingFacade object will parse the xml file attached to the mediator
        in the property mediator.junit_xml_file_path

        Args:
            mediator (ZigZag): the mediator that stores shared data
        """
        self._mediator = mediator

    def parse(self):
        """Read and validate the input file contents.
        sets the property 'junit_xml' on the mediator
        sets the property 'test_suite_props' on the mediator
        sets the property 'build_url' on the mediator
        sets the property 'build_number' on the mediator

        Raises:
            RuntimeError: invalid path.
            RuntimeError: The file does not contain valid XML!.
            RuntimeError: Test suite is missing the required property!
        """

        root_element = 'testsuite'
        junit_xsd = pytest_rpc.get_xsd()
        file_path = self._mediator.junit_xml_file_path

        try:
            if os.path.getsize(file_path) > self._MAX_FILE_SIZE:
                raise RuntimeError("Input file '{}' is larger than allowed max file size!".format(file_path))

            junit_xml_doc = etree.parse(file_path)
        except (IOError, OSError):
            raise RuntimeError("Invalid path '{}' for JUnitXML results file!".format(file_path))
        except etree.ParseError:
            raise RuntimeError("The file '{}' does not contain valid XML!".format(file_path))

        try:
            xmlschema = etree.XMLSchema(etree.parse(junit_xsd))
            xmlschema.assertValid(junit_xml_doc)
            junit_xml = junit_xml_doc.getroot()
        except etree.DocumentInvalid as e:
            debug = "\n\n---DEBUG XML PRETTY PRINT---\n\n"
            error_message = "The file '{}' does not conform to schema!" \
                            "\n\nSchema Violation:\n{}".format(file_path, str(e))
            if self._mediator.pprint_on_fail:
                error_message = "{0}{1}{2}{1}".format(error_message,
                                                      debug,
                                                      etree.tostring(junit_xml_doc, pretty_print=True))
            raise RuntimeError("The file '{}' does not conform to schema!"
                               "\n\nSchema Violation:\n{}".format(file_path, error_message))

        if junit_xml.tag != root_element:
            raise RuntimeError("The file '{}' does not have JUnitXML '{}' root element!".format(file_path, root_element))  # noqa

        self._mediator.junit_xml = junit_xml
        self._mediator.testsuite_props = {
            p.attrib['name']: p.attrib['value'] for p in self._mediator.junit_xml.findall('./properties/property')}
        self._mediator.serialized_junit_xml = etree.tostring(junit_xml, encoding='UTF-8', xml_declaration=True)
        try:
            self._mediator.build_url = self._mediator.testsuite_props['BUILD_URL']
            self._mediator.build_number = self._mediator.testsuite_props['BUILD_NUMBER']
        except KeyError as e:
            raise RuntimeError("Test suite is missing the required property!\n\n{}".format(str(e)))
        for testcase_xml in self._mediator.junit_xml.findall('testcase'):
            TestLog(testcase_xml, self._mediator)  # new test logs attach themselves to the mediator
