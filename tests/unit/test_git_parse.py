# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import re
import pytest
import swagger_client
from hashlib import md5
from zigzag.zigzag import ZigZag
from swagger_client.rest import ApiException
import requests
import json
from zigzag.git_repo_parsing_facade import GitRepoParsingFacade

# ======================================================================================================================
# Test Suites
# ======================================================================================================================


class TestZigZagGitParse(object):

    def test_do_it(self):
        """verify that the ZigZag object stores properties after initialization"""

        api_token = ''
        project_id = '71096'

        zz = ZigZag(None, api_token, project_id, None)

        path = '/Users/zach2872/repos/molecule-validate-cinder-deploy/molecule/default/tests'

        grpf = GitRepoParsingFacade(zz)
        grpf.parse(path)
        grpf.upload_cases_to_qtest()
