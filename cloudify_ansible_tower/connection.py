# #######
# Copyright (c) 2020 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    Connection
    ~~~~~~~~~~
    Ansible Tower REST API connection helpers
"""

# Py3 Compatibility

import json
import requests
from requests.packages import urllib3

from cloudify import ctx
from cloudify_ansible_tower import utils


class Connection(object):
    """
        Connection handler for the Ansible Tower REST API

    :param `logging.Logger` logger:
        Logger for the class to use. Defaults to `ctx.logger`
    """
    def __init__(self, api_version='v2', logger=None, _ctx=ctx):
        # Set the active context
        self.ctx = _ctx
        self.api_version = api_version
        # Configure logger
        self.log = utils.create_child_logger(
            'connection',
            plogger=logger)
        # Get credentials object
        self.creds = utils.get_credentials(_ctx=self.ctx)
        # Get a pre-configured requests.Session object
        self.session = self.get_session_connection()

    def __del__(self):
        # Clean up any Session connections
        if self.session:
            self.session.close()

    def request(self, **kwargs):
        """
            Builds, and executes, a request to the
            Ansible Tower API service.  The parameters
            are passed as-is to the underlying
            requests.Session.request() function.

        :returns: A configured requests.Session instance
        :rtype: :class:`requests.Response`
        """
        # Rework the URL
        url = kwargs.pop('url', '')
        # Check if this is a relative operation
        if url.startswith('/'):
            # Add the endpoint and subscription ID
            url = self.creds.endpoint + url
        kwargs['url'] = url
        # Log the request details
        self.log.info('request({0})'.format(kwargs))
        res = self.session.request(**kwargs)
        # Only get data if there's data to be gotten
        data = None
        if res.text:
            data = res.json()
        self.log.debug('response: '
                       '(status={0}, data={1})'.format(
                           res.status_code,
                           json.dumps(data, indent=2)))
        return res

    def get_session_connection(self):
        """
            Creates a `requests.Session` instance with
            an API access token and includes basic
            connection fault tolerance.

        :returns: A configured requests.Session instance
        :rtype: :class:`requests.Session`
        """
        # Build a session object with some fault tolerance
        # Retry up to 10 times with increasing backoff time
        # up to 120 seconds.
        session = requests.Session()
        session.mount(
            self.creds.endpoint,
            requests.adapters.HTTPAdapter(
                max_retries=urllib3.util.Retry(
                    total=10,
                    backoff_factor=0.4,
                    status_forcelist=[500, 501, 502, 503, 504]
                )))
        # SSL Verification
        if not self.creds.endpoint.startswith('http://'):
            session.verify = self.creds.endpoint_verify
        # Set the API access token for the session
        session.headers = {
            'Authorization': 'Bearer {0}'.format(
                self.creds.access_token),
            'Content-Type': 'application/json'
        }
        return session
