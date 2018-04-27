# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import os
import re
import pytest_rpc
import swagger_client
from lxml import etree
from base64 import b64encode
from datetime import datetime
from swagger_client.rest import ApiException


# ======================================================================================================================
# Globals
# ======================================================================================================================
TESTCASE_NAME_RGX = re.compile(r'(\w+)(\[.+\])')
TESTCASE_GROUP_RGX = re.compile(r'tests\.(test_[\w-]+)\.?(Test\w+)?$')
MAX_FILE_SIZE = 52428800


# ======================================================================================================================
# Functions
# ======================================================================================================================
def _load_input_file(file_path, pprint_on_fail=False):
    """Read and validate the input file contents.

    Args:
        file_path (str): A string representing a valid file path.
        pprint_on_fail (bool): A flag for enabling debug pretty print on schema failure.

    Returns:
        ElementTree: An ET object already pointed at the root "testsuite" element.

    Raises:
        RuntimeError: invalid path.
    """

    root_element = 'testsuite'
    junit_xsd = pytest_rpc.get_xsd()

    try:
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
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
        if pprint_on_fail:
            error_message = "{0}{1}{2}{1}".format(error_message,
                                                  debug,
                                                  etree.tostring(junit_xml_doc, pretty_print=True))
        raise RuntimeError("The file '{}' does not conform to schema!"
                           "\n\nSchema Violation:\n{}".format(file_path, error_message))

    if junit_xml.tag != root_element:
        raise RuntimeError("The file '{}' does not have JUnitXML '{}' root element!".format(file_path, root_element))

    return junit_xml


def _generate_module_hierarchy(testcase_xml, testsuite_props):
    """Construct a qTest swagger model for all the JUnitXML test cases.

    Args:
        testcase_xml (ElementTree): A XML element representing a JUnit style testcase result.
        testsuite_props (dict): Global properties from the associated testsuite for the given testcase result.

    Returns:
        list(str): An ordered list of strings to use for the qTest results hierarchy.

    Raises:
        KeyError: missing test suite property.
        AttributeError: the testcase 'classname' attribute is invalid
    """

    module_hierarchy = [testsuite_props['RPC_RELEASE'],             # RPC Release Version (e.g. 16.0.0)
                        testsuite_props['JOB_NAME'],                # CI Job name (e.g. PM_rpc-openstack-pike-xenial_mnaio_no_artifacts-swift-system) # noqa
                        testsuite_props['MOLECULE_TEST_REPO'],      # (e.g. molecule-validate-neutron-deploy)
                        testsuite_props['MOLECULE_SCENARIO_NAME']]  # (e.g. "default")

    testcase_groups = TESTCASE_GROUP_RGX.search(testcase_xml.attrib['classname']).groups()

    module_hierarchy.append(testcase_groups[0])         # Always append at least the filename of the test grouping.
    if testcase_groups[1]:
        module_hierarchy.append(testcase_groups[1])     # Append the class name of tests if specified.

    return module_hierarchy


def _generate_test_logs(junit_xml):
    """Construct a qTest swagger model for all the JUnitXML test cases.

    Args:
        junit_xml (ElementTree): A XML element representing a JUnit style testsuite result.

    Returns:
        list(AutomationTestLogResource): A list of qTest swagger model test logs.
    """

    serialized_junit_xml = etree.tostring(junit_xml, encoding='UTF-8', xml_declaration=True)
    testsuite_props = {p.attrib['name']: p.attrib['value'] for p in junit_xml.findall('./properties/property')}
    date_time_now = datetime.utcnow()
    test_logs = []

    for testcase_xml in junit_xml.findall('testcase'):
        testcase_status = 'PASSED'

        if testcase_xml.find('failure') is not None or testcase_xml.find('error') is not None:
            testcase_status = 'FAILED'
        elif testcase_xml.find('skipped') is not None:
            testcase_status = 'SKIPPED'

        test_log = swagger_client.AutomationTestLogResource()

        try:
            test_log.name = TESTCASE_NAME_RGX.match(testcase_xml.attrib['name']).group(1)
            test_log.automation_content = testcase_xml.find("./properties/property/[@name='test_id']").attrib['value']
            test_log.exe_start_date = testcase_xml.find("./properties/property/[@name='start_time']").attrib['value']
            test_log.exe_end_date = testcase_xml.find("./properties/property/[@name='end_time']").attrib['value']
        except AttributeError:
            raise RuntimeError("Test case '{}' is missing the required property!".format(test_log.name))

        try:
            test_log.build_url = testsuite_props['BUILD_URL']
            test_log.build_number = testsuite_props['BUILD_NUMBER']
            test_log.module_names = _generate_module_hierarchy(testcase_xml, testsuite_props)
        except KeyError as e:
            raise RuntimeError("Test suite is missing the required property!\n\n{}".format(str(e)))
        except AttributeError:
            raise RuntimeError("Test case '{}' has an invalid 'classname' attribute!".format(test_log.name))

        test_log.status = testcase_status
        test_log.attachments = \
            [swagger_client.AttachmentResource(name="junit_{}.xml".format(date_time_now.strftime('%Y-%m-%dT%H-%M')),
                                               content_type='application/xml',
                                               data=b64encode(serialized_junit_xml).decode('UTF-8'),
                                               author={})]
        test_logs.append(test_log)

    return test_logs


def _generate_auto_request(junit_xml, test_cycle):
    """Construct a qTest swagger model for a JUnitXML test run result. (Called an "automation request" in
    qTest parlance)

    Args:
        junit_xml (ElementTree): A XML element representing a JUnit style testsuite result.
        test_cycle (str): The parent qTest test cycle for test results.

    Returns:
        AutomationRequest: A qTest swagger model for an automation request.
    """

    auto_req = swagger_client.AutomationRequest()
    auto_req.test_cycle = test_cycle
    auto_req.test_logs = _generate_test_logs(junit_xml)
    auto_req.execution_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')   # UTC timezone 'Zulu'

    return auto_req


def upload_test_results(junit_xml_file_path, qtest_api_token, qtest_project_id, qtest_test_cycle, pprint_on_fail=False):
    """Construct a 'AutomationRequest' qTest resource and upload the test results to the desired project in
    qTest Manager.

    Args:
        junit_xml_file_path (str): A file path to a XML element representing a JUnit style testsuite response.
        qtest_api_token (str): Token to use for authorization to the qTest API.
        qtest_project_id (int): The target qTest project for the test results.
        qtest_test_cycle (str): The parent qTest test cycle for test results. (e.g. Product Release codename "Queens")
        pprint_on_fail (bool): A flag for enabling debug pretty print on schema failure.

    Returns:
        int: The queue processing ID for the job.

    Raises:
        RuntimeError: Failed to upload test results to qTest Manager.
    """

    junit_xml = _load_input_file(junit_xml_file_path, pprint_on_fail)

    swagger_client.configuration.api_key['Authorization'] = qtest_api_token
    auto_api = swagger_client.TestlogApi()
    auto_req = _generate_auto_request(junit_xml, qtest_test_cycle)

    try:
        response = auto_api.submit_automation_test_logs_0(project_id=qtest_project_id,
                                                          body=auto_req,
                                                          type='automation')
    except ApiException as e:
        raise RuntimeError("The qTest API reported an error!\n"
                           "Status code: {}\n"
                           "Reason: {}\n"
                           "Message: {}".format(e.status, e.reason, e.body))
    if response.state == 'FAILED':
        raise RuntimeError("The qTest API failed to process the job!\nJob ID: {}".format(response.id))

    return int(response.id)
