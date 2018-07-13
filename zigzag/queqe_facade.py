# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================

import swagger_client
from swagger_client.rest import ApiException


class QueueFacade(object):

    def __init__(self):
        self.queue_api = swagger_client.TestlogApi()

    def check_status(self, queue_processing_id):
        """Check the status of a qTest test log submission

        Args:
            queue_processing_id (int): The ID of the submission job

        Returns:
            Str: The current state of the submission job

        Raises:
            RuntimeError: The qTest API reported an error!.
        """
        try:
            response = self.queue_api.track(queue_processing_id)
            return response.state
        except ApiException as e:
            raise RuntimeError("The qTest API reported an error!\n"
                               "Status code: {}\n"
                               "Reason: {}\n"
                               "Message: {}".format(e.status, e.reason, e.body))
