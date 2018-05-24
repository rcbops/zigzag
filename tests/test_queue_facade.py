#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import swagger_client
from zigzag.queqe_facade import QueueFacade


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestQueueFacade(object):
    """Test cases for the 'QueueFacade' class"""

    def test_good_id(self, mocker):
        """Verify that a good ID will return a status"""

        # Mock
        mock_queue_resp = mocker.Mock(spec=swagger_client.QueueProcessingResponse)
        mock_queue_resp.state = 'SUCCESS'
        mocker.patch('swagger_client.TestlogApi.track', return_value=mock_queue_resp)

        # Setup
        job_id = 12345
        qf = QueueFacade()
        status = qf.check_status(job_id)

        # Test
        assert status == 'SUCCESS'

    def test_bad_id(self, mocker):
        # I'm not sure what this will look like
        pass
