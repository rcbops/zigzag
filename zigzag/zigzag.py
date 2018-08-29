# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import swagger_client
from datetime import datetime
from swagger_client.rest import ApiException
from zigzag.utility_facade import UtilityFacade
from zigzag.xml_parsing_facade import XmlParsingFacade
from zigzag.requirements_link_facade import RequirementsLinkFacade


class ZigZag(object):

    def __init__(self, junit_xml_file_path, qtest_api_token, qtest_project_id, qtest_test_cycle, pprint_on_fail=False):
        """ Create a ZigZag facade class object. The ZigZag class uses the Facade pattern to call out to
        subsystems and sub Facades.

        Args:
           junit_xml_file_path (str): A file path to a XML element representing a JUnit style testsuite response.
           qtest_api_token (str): Token to use for authorization to the qTest API.
           qtest_project_id (int): The target qTest project for the test results.
           qtest_test_cycle (str): The parent qTest test cycle for test results. (e.g. Product Release codename "Queens")
           pprint_on_fail (bool): A flag for enabling debug pretty print on schema failure.
        """  # noqa

        swagger_client.configuration.api_key['Authorization'] = qtest_api_token
        self._qtest_api_token = qtest_api_token
        self._junit_xml_file_path = junit_xml_file_path
        self._qtest_project_id = qtest_project_id
        self._qtest_test_cycle = qtest_test_cycle
        self._pprint_on_fail = pprint_on_fail
        self._test_logs = []

        # properties that will be written to an instance of this class as a mediator
        self._ci_environment = None
        self._build_number = None
        self._build_url = None
        self._testsuite_props = None
        self._serialized_junit_xml = None
        self._junit_xml = None
        self._junit_xml_doc = None

        self._utility_facade = UtilityFacade(self)
        self._parsing_facade = XmlParsingFacade(self)
        self._requirement_link_facade = RequirementsLinkFacade(self)

    #  properties with only getters
    @property
    def qtest_api_token(self):
        """Gets the qTest API token

        Returns:
            str: The qTest API token
        """
        return self._qtest_api_token

    @property
    def junit_xml_file_path(self):
        """Gets the junit XML file path

        Returns:
            str: The file path for the junit xml file
        """
        return self._junit_xml_file_path

    @property
    def qtest_project_id(self):
        """Gets the qTest project ID

        Returns:
             int: The qTest project ID
        """
        return self._qtest_project_id

    @property
    def qtest_test_cycle(self):
        """Gets the qTest test cycle

        Returns:
            str: The qTest test cycle
        """
        return self._qtest_test_cycle

    @qtest_test_cycle.setter
    def qtest_test_cycle(self, value):
        """Sets the qTest test cycle
        """
        self._qtest_test_cycle = value

    @property
    def pprint_on_fail(self):
        """Get the pprint value

        Returns:
            bool: If zigzag should pprint
        """
        return self._pprint_on_fail

    @property
    def test_logs(self):
        """Gets the test log objects

        Returns:
            list(TestLog): A list of TestLog objects
        """
        return self._test_logs

    #  properties with setters and getters
    @property
    def build_url(self):
        """Gets the build_url

        Returns:
            str: The url for the build
        """
        return self._build_url

    @build_url.setter
    def build_url(self, value):
        """Sets the value for build_url
        """
        self._build_url = value

    @property
    def build_number(self):
        """Gets the value for build_number

        Returns:
            int: the number of the build
        """
        return self._build_number

    @build_number.setter
    def build_number(self, value):
        """Sets the number of the build
        """
        self._build_number = value

    @property
    def testsuite_props(self):
        """Gets the value for testsuite_props

        Returns:
            dict: the properties of the testsuite
        """
        return self._testsuite_props

    @testsuite_props.setter
    def testsuite_props(self, value):
        """Sets the properties of the testsuite"""
        self._testsuite_props = value

    @property
    def junit_xml(self):
        """Gets the junit xml

        Returns:
            ElementTree: The junit xml element tree
        """
        return self._junit_xml

    @junit_xml.setter
    def junit_xml(self, value):
        """Sets the junit xml
        """
        self._junit_xml = value

    @property
    def junit_xml_doc(self):
        """Gets the junit_xml_doc

        Returns:
            ElementTree: The junit xml element tree
        """
        return self._junit_xml_doc

    @junit_xml_doc.setter
    def junit_xml_doc(self, value):
        """Sets the junit_xml_doc
        """
        self._junit_xml_doc = value

    @property
    def serialized_junit_xml(self):
        """Gets the serialized junit xml

        Returns:
            str: The serialized junit xml
        """
        return self._serialized_junit_xml

    @serialized_junit_xml.setter
    def serialized_junit_xml(self, value):
        """Sets the serialized junit xml"""
        self._serialized_junit_xml = value

    @property
    def ci_environment(self):
        """Gets the configured test_runner

        Returns:
            str: the configured ci_environment
        """
        return self._ci_environment

    @ci_environment.setter
    def ci_environment(self, value):
        """Sets the configured ci_environment"""
        self._ci_environment = value

    def _generate_auto_request(self):
        """Construct a qTest swagger model for a JUnitXML test run result. (Called an "automation request" in
        qTest parlance)

        Returns:
            AutomationRequest: A qTest swagger model for an automation request.
        """

        auto_req = swagger_client.AutomationRequest()
        auto_req.test_logs = [log.qtest_test_log for log in self._test_logs]
        auto_req.test_cycle = \
            self._utility_facade.discover_parent_test_cycle(self.qtest_test_cycle)
        auto_req.execution_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')   # UTC timezone 'Zulu'

        return auto_req

    def upload_test_results(self):
        """Construct a 'AutomationRequest' qTest resource and upload the test results to the desired project in
        qTest Manager.

        Returns:
            int: The queue processing ID for the job.

        Raises:
            RuntimeError: Failed to upload test results to qTest Manager.
        """  # noqa

        auto_api = swagger_client.TestlogApi()
        auto_req = self._generate_auto_request()

        try:
            response = auto_api.submit_automation_test_logs_0(project_id=self._qtest_project_id,
                                                              body=auto_req,
                                                              type='automation')
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))
        if response.state == 'FAILED':
            raise RuntimeError("The qTest API failed to process the job!\nJob ID: {}".format(response.id))

        # for now we will always try to link the cases
        # this should move somewhere else in the future or be optional to this
        self._requirement_link_facade.link()

        return int(response.id)

    def parse(self):
        """Parse the xml"""

        self._parsing_facade.parse()  # this was moved from the init method
