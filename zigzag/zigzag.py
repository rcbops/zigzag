# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import re
import swagger_client
import xml.etree.ElementTree as Etree
from datetime import datetime
from swagger_client.rest import ApiException


# ======================================================================================================================
# Globals
# ======================================================================================================================
TESTCASE_NAME_RGX = re.compile(r'(\w+)(\[.+\])')


# ======================================================================================================================
# Functions
# ======================================================================================================================
def _load_input_file(file_path):
    """Read and validate the input file contents.

    Args:
        file_path (str): A string representing a valid file path.

    Returns:
        ElementTree: An ET object already pointed at the root "testsuite" element.

    Raises:
        RuntimeError: invalid path.
    """

    root_element = "testsuite"

    try:
        junit_xml = Etree.parse(file_path).getroot()
    except IOError:
        raise RuntimeError('Invalid path "{}" for JUnitXML results file!'.format(file_path))
    except Etree.ParseError:
        raise RuntimeError('The file "{}" does not contain valid XML!'.format(file_path))

    if junit_xml.tag != root_element:
        raise RuntimeError('The file "{}" does not have JUnitXML "{}" root element!'.format(file_path, root_element))

    return junit_xml


def _generate_test_log(junit_testcase_xml, testsuite_props):
    """Construct a qTest swagger model for a single JUnitXML test result.

    Args:
        junit_testcase_xml (ElementTree): A XML element representing a JUnit style testcase result.
        testsuite_props (dict): A dictionary of properties for the testsuite from within which the testcase executed.

    Returns:
        AutomationTestLogResource: A qTest swagger model for an test log.
    """

    testcase_status = 'PASSED'

    if junit_testcase_xml.find('failure') is not None or junit_testcase_xml.find('error') is not None:
        testcase_status = 'FAILED'
    elif junit_testcase_xml.find('skipped') is not None:
        testcase_status = 'SKIPPED'

    test_log = swagger_client.AutomationTestLogResource()

    test_log.name = TESTCASE_NAME_RGX.match(junit_testcase_xml.attrib['name']).group(1)
    test_log.status = testcase_status
    test_log.module_names = [testsuite_props['GIT_BRANCH']]                      # GIT_BRANCH == RPC release
    test_log.exe_start_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')   # UTC timezone 'Zulu'
    test_log.exe_end_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')     # UTC timezone 'Zulu'
    test_log.automation_content = junit_testcase_xml.find("./properties/property/[@name='test_id']").attrib['value']

    return test_log


def _generate_auto_request(junit_xml, test_cycle):
    """Construct a qTest swagger model for a JUnitXML test run result. (Called an "automation request" in
    qTest parlance)

    Args:
        junit_xml (ElementTree): A XML element representing a JUnit style testsuite result.
        test_cycle (str): The parent qTest test cycle for test results.

    Returns:
        AutomationRequest: A qTest swagger model for an automation request.
    """

    testsuite_props = {p.attrib['name']: p.attrib['value'] for p in junit_xml.findall('./properties/property')}
    test_logs = [_generate_test_log(tc_xml, testsuite_props) for tc_xml in junit_xml.findall('testcase')]

    auto_req = swagger_client.AutomationRequest()
    auto_req.test_cycle = test_cycle
    auto_req.test_logs = test_logs
    auto_req.execution_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')   # UTC timezone 'Zulu'

    return auto_req


def upload_test_results(junit_xml_file_path, qtest_api_token, qtest_project_id, qtest_test_cycle):
    """Construct a 'AutomationRequest' qTest resource and upload the test results to the desired project in
    qTest Manager.

    Args:
        junit_xml_file_path (str): A file path to a XML element representing a JUnit style testsuite response.
        qtest_api_token (str): Token to use for authorization to the qTest API.
        qtest_project_id (int): The target qTest project for the test results.
        qtest_test_cycle (str): The parent qTest test cycle for test results.

    Returns:
        int: The queue processing ID for the job.

    Raises:
        RuntimeError: Failed to upload test results to qTest Manager.
    """

    junit_xml = _load_input_file(junit_xml_file_path)

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
