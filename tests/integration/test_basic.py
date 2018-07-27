# -*- coding: utf-8 -*-

"""Basic functionality tests for proving that ZigZag can publish results to qTest accurately."""


def test_publish_asc_single_passing(single_passing_test_for_asc):
    """Verify that the CLI will process required arguments and environment variables. (All uploading of test
    results has been mocked)
    """

    single_passing_test_for_asc.assert_invoke_zigzag()


def test_publish_mk8s_single_passing(single_passing_test_for_mk8s):
    """Verify that the CLI will process required arguments and environment variables. (All uploading of test
    results has been mocked)"""

    single_passing_test_for_mk8s.assert_invoke_zigzag()
