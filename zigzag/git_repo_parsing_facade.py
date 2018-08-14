# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================

from __future__ import absolute_import
import os
from zigzag.zigzag_test_case import ZigZagTestCase
from zigzag.zigzag_git_branch import ZigZagGitBranch
from zigzag.zigzag_git_source import ZigZagGitSource
import ast
import re
import git
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint


class GitRepoParsingFacade(object):

    def __init__(self, mediator):
        self._mediator = mediator
        self._source = ZigZagGitSource(mediator)

    def parse(self, path):
        """Parse the files on disk
        """
        repo = git.Repo('/Users/zach2872/repos/molecule-validate-cinder-deploy')
        heads = repo.git.ls_remote(h='origin').split('\n')
        branches = {}
        for head in heads:
            x = str(head).split('\trefs/heads/')
            branches[x[1]] = x[0]
        test_cases = {}
        # TODO add logic for changing branches and storeing data from them

        for name, sha in list(branches.items()):
            repo.git.checkout(sha)
            for file_path in self._find_test_files(path):
                with open(file_path) as f:
                    for node in ast.walk(ast.parse(f.read())):
                        if isinstance(node, ast.FunctionDef) and re.match(r'^test_', node.name):
                            zztc = ZigZagTestCase(node, name, file_path, self._mediator)
                            test_cases[zztc.test_id] = zztc
            self._source.add_branch(ZigZagGitBranch(name, sha, test_cases))

    def upload_cases_to_qtest(self):
        """This one is a hack too
        It will find all unique cases and create a link to them on the case
        """

        # create an instance of the API class
        api_instance = swagger_client.TestcaseApi()
        project_id = self._mediator.qtest_project_id

        for test_id, test_case in self._source.reduced_tests.items():
            body = swagger_client.TestCaseWithCustomFieldResource()
            body.properties = [swagger_client.PropertyResource(field_id=test_case.automation_content_field_id,
                                                               field_value=test_case.test_id),
                               swagger_client.PropertyResource(field_id=4837454,  # automation = true
                                                               field_value=711),
                               swagger_client.PropertyResource(field_id=4837458,  # type
                                                               field_value=702)]  # this seems like some secret sauce
            body.name = test_case.name

            # a hack to format the links :)
            links = ''
            for branch, link in test_case.git_links.items():
                links = links + '<p><a href="{}">{}</a></p>'.format(link, branch.name)


            description = """
            <p>{}</p>
            
            <p>Here are the links to this test case on every branch it exists on
            {}
            </p>
            """.format(test_case.description, links)
            body.description = description  # TODO why do newlines not work???
            body.test_steps = []
            # TODO attach test steps here

            for step in test_case.test_steps:
                body.test_steps.append(swagger_client.TestStepResource(description=step,
                                                                       expected='pass'))
            try:
                # Creates a Test Case
                api_response = api_instance.create_test_case(project_id, body)
            except ApiException as e:
                raise RuntimeError('There was an error in creating a test case')

    def _find_test_files(self, path):
        regex = re.compile(r'test_.*\.py')

        def filter_tests(root, files):
            test_files = []
            for f in files:
                if regex.match(f):
                    test_files.append(os.path.join(root, f))
            return test_files

        def recurse(recurse_pat):
            try:
                test_files  # there has to be a better way to do this
            except NameError:
                test_files = []
            walk_dir = os.path.abspath(recurse_pat)
            for root, subdirs, files in os.walk(walk_dir):
                for subdir in subdirs:
                    test_files = recurse(subdir)
                    test_files = filter_tests(root, files) + test_files
                test_files = filter_tests(root, files) + test_files
            return test_files

        return recurse(path)

