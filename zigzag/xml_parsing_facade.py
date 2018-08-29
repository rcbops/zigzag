# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================

from __future__ import absolute_import
import os
from lxml import etree
from zigzag.zigzag_test_log import ZigZagTestLog
import pkg_resources


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

    def _determine_ci_environment(self):
        """Determines the ci-environment that was used to create the junit xml file"""
        try:
            ci_environment = self._mediator.junit_xml.find(
                "./properties/property/[@name='ci-environment']").attrib['value']
            self._mediator.ci_environment = ci_environment
        except AttributeError:
            self._mediator.ci_environment = 'asc'  # hard code this here

    def _read(self):
        """Read the input file contents
        sets the property 'serialized_junit_xml' & 'junit_xml'on the mediator

        Raises:
            RuntimeError: invalid path.
            RuntimeError: The file does not contain valid XML!.
            RuntimeError: Test suite is missing the required property!
        """

        file_path = self._mediator.junit_xml_file_path
        try:
            junit_xml_doc = etree.parse(file_path)
            junit_xml = junit_xml_doc.getroot()
            if os.path.getsize(file_path) > self._MAX_FILE_SIZE:
                raise RuntimeError("Input file '{}' is larger than allowed max file size!".format(file_path))
        except (IOError, OSError):
            raise RuntimeError("Invalid path '{}' for JUnitXML results file!".format(file_path))
        except etree.ParseError:
            raise RuntimeError("The file '{}' does not contain valid XML!".format(file_path))

        self._mediator.junit_xml = junit_xml
        self._mediator.serialized_junit_xml = etree.tostring(junit_xml, encoding='UTF-8', xml_declaration=True)
        self._mediator.junit_xml_doc = junit_xml_doc

    def _validate(self):
        """Validate the input file contents.

        Raises:
            RuntimeError: "The file does not conform to schema!"
            RuntimeError: The file does not have JUnitXML root element!
        """

        root_element = 'testsuite'
        junit_xsd = self._get_xsd(self._mediator.ci_environment)
        file_path = self._mediator.junit_xml_file_path

        try:
            xmlschema = etree.XMLSchema(etree.parse(junit_xsd))
            xmlschema.assertValid(self._mediator.junit_xml_doc)
        except etree.DocumentInvalid as e:
            debug = "\n\n---DEBUG XML PRETTY PRINT---\n\n"
            error_message = "The file '{}' does not conform to schema!" \
                            "\n\nSchema Violation:\n{}".format(file_path, str(e))
            if self._mediator.pprint_on_fail:
                error_message = "{0}{1}{2}{1}".format(error_message,
                                                      debug,
                                                      etree.tostring(self._mediator.junit_xml_doc, pretty_print=True))
            raise RuntimeError("The file '{}' does not conform to schema!"
                               "\n\nSchema Violation:\n{}".format(file_path, error_message))

        if self._mediator.junit_xml.tag != root_element:
            raise RuntimeError("The file '{}' does not have JUnitXML '{}' root element!".format(
                file_path, root_element))

    def _get_xsd(self, ci_environment='asc'):
        """Retrieve a XSD for validating JUnitXML results produced by this plug-in.

        Args:
            ci_environment (str): the value found in the ci-environment global property from the XML

        Returns:
            io.BytesIO: A file like stream object.

        Raises:
            RuntimeError: 'Unknown ci-environment'
        """

        if ci_environment == 'asc':
            return pkg_resources.resource_stream('zigzag', 'data/molecule_junit.xsd')
        elif ci_environment == 'mk8s':
            return pkg_resources.resource_stream('zigzag', 'data/mk8s_junit.xsd')
        else:
            raise RuntimeError("Unknown ci-environment '{}'".format(ci_environment))
