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
    resources.Base
    ~~~~~~~~~~~~~~
    Ansible Tower API abstraction layer
"""

import json
import yaml
import requests

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError, RecoverableError

from cloudify_ansible_tower import connection, utils


class Resource(object):
    """
        Ansible Tower base resource interface
    .. warning::
        This interface should only be instantiated from
        within a Cloudify Lifecycle Operation
    :param string name: Human-readable name of the child resource
    :param string endpoint: Partial endpoint for making resource requests
    :param `logging.Logger` logger:
        Parent logger for the class to use. Defaults to `ctx.logger`
    :param object _ctx: Cloudify Context object with *node* and
        *instance* properties. This is used to override the global
        *ctx* object to handle situations such as relationship
        operations where a source or target interface is used instead
        of a global one
    """
    def __init__(self, name, endpoint, _id=None,
                 lookup=['id'], logger=None, _ctx=ctx):
        # Set the active context
        self.ctx = _ctx
        # Configure logger
        self.log = utils.create_child_logger(
            'resources.{0}'.format(name.replace(' ', '')),
            plogger=logger)
        # Set up labeling
        self.name = name
        self.lookup = lookup
        # Build the partial endpoint
        self.endpoint = endpoint
        self.api_version = 'v2'
        # Get a connection
        self.client = connection.Connection(
            logger=self.log,
            _ctx=self.ctx)
        self._id = _id

    @property
    def resource_id(self):
        if self._id:
            return self._id
        self._id = self.lookup_id(
            utils.get_resource_name(_ctx=self.ctx))
        return self._id

    @resource_id.setter
    def resource_id(self, name):
        self._id = name

    @property
    def resource_url(self):
        return '{0}/{1}{2}/{3}/'.format(
            '/api', self.api_version, self.endpoint, self.resource_id)

    @property
    def collection_url(self):
        return '{0}/{1}{2}/'.format('/api', self.api_version, self.endpoint)

    def exists(self):
        """
            Checks if a resource exists
        :returns: True if resource exists
        :rtype: boolean
        """
        if not self.resource_id:
            raise RecoverableError(
              '{0}.exists() used without ID!'.format(self.name))
        self.log.info('Retrieving {0} "{1}"'.format(
            self.name, self.resource_id))

        # Make the request
        res = self.client.request(method='get', url=self.resource_url)
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        headers = self.lowercase_headers(res.headers)
        # Check the response
        # HTTP 200 (OK) - The resource already exists
        if res.status_code == requests.codes.ok:
            return True
        return False

    def list(self):
        """
            Lists resources of a type
        :param string name: Name of the resource type
        :returns: list of resources
        :rtype: list
        """
        self.log.info('Retrieving {0} resources'.format(self.name))
        # Make the request
        res = self.client.request(method='get', url=self.collection_url)
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        headers = self.lowercase_headers(res.headers)
        # Check the response
        # HTTP 200 (OK) - The resource already exists
        if res.status_code == requests.codes.ok:
            return res.json()
        return list()

    def get(self):
        """
            Gets details about an existing resource
        :returns: Response data from the API call
        :rtype: dict
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`,
                 :exc:`requests.RequestException`
        """
        self.log.info('Retrieving {0} "{1}"'.format(
            self.name, self.resource_id))
        # Make the request
        res = self.client.request(method='get', url=self.resource_url)
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        headers = self.lowercase_headers(res.headers)
        # Check the response
        # HTTP 200 (OK) - The resource already exists
        if res.status_code == requests.codes.ok:
            return res.json()
        # If API sent a 400, we're sending bad data
        if res.status_code == requests.codes.bad_request:
            self.log.info('BAD REQUEST: response: {}'.format(res.content))
            raise NonRecoverableError(
                '{0} "{1}" BAD REQUEST'
                .format(self.name, self.resource_id))
        # If API sent a 404, the resource doesn't exist (yet?)
        if res.status_code == requests.codes.not_found:
            raise RecoverableError(
                '{0} "{1}" doesn\'t exist (yet?)'
                .format(self.name, self.resource_id))
        # All other errors will be treated as recoverable
        raise RecoverableError(
            'Expected HTTP status code {0}, recieved {1}'
            .format(requests.codes.ok, res.status_code))

    def create(self, params):
        """
            Creates a new resource
        :param dict params: Parameters to be passed as-is to the API
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`,
                 :exc:`requests.RequestException`
        """
        self.log.info('Creating new {0}'.format(self.name))
        # Sanitize input data
        kwargs = params.pop('kwargs', dict())
        params = utils.dict_update(params, kwargs)
        params = self.sanitize_json_input(params)

        # Make the request
        res = self.client.request(
            method='post', url=self.collection_url, json=params)
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        headers = self.lowercase_headers(res.headers)
        # Check the response
        # If API sent a 400, we're sending bad data
        if res.status_code == requests.codes.bad_request:
            self.log.info('BAD REQUEST: response: {}'.format(res.content))
            raise NonRecoverableError(
                '{0} BAD REQUEST'.format(self.name))
        # All other errors will be treated as recoverable
        if res.status_code != requests.codes.created:
            raise RecoverableError(
                'Expected HTTP status code {0}, recieved {1}'
                .format(requests.codes.created, res.status_code))
        return res.json()

    def delete(self):
        """
            Deletes an existing resource
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`,
                 :exc:`requests.RequestException`
        """
        self.log.info('Deleting {0} "{1}"'.format(
            self.name, self.resource_id))

        # Make the request
        res = self.client.request(method='delete', url=self.resource_url)
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        headers = self.lowercase_headers(res.headers)
        # Check the response
        # If API sent 204, we're good
        if res.status_code in [requests.codes.no_content, requests.codes.accepted]:
            return
        # If API sent a 400, we're sending bad data
        if res.status_code == requests.codes.bad_request:
            self.log.info('BAD REQUEST: response: {}'.format(res.content))
            raise NonRecoverableError(
                '{0} "{1}" BAD REQUEST'
                .format(self.name, self.resource_id))
        # All other errors will be treated as recoverable
        raise RecoverableError(
            'Expected HTTP status code {0}, recieved {1}'
            .format(requests.codes.no_content, res.status_code))

    def lookup_id(self, name):
        """
            Find a resource's ID
        :param string name: Name/ID of the existing resource
        :returns: Resource ID
        :rtype: integer
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`,
                 :exc:`requests.RequestException`
        """
        self.log.info('Retrieving list {0}'.format(self.name))
        # Make the request
        res = self.client.request(method='get', url=self.collection_url)
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        headers = self.lowercase_headers(res.headers)
        # Check the response
        # HTTP 200 (OK) - The resource already exists
        if res.status_code != requests.codes.ok:
            raise RecoverableError(
                'Expected HTTP status code {0}, recieved {1}'
                .format(requests.codes.ok, res.status_code))
        # Get list of resources
        obj = None
        for r_obj in res.json().get('results', list()):
            for lookup in self.lookup:
                if name == r_obj.get(lookup):
                    return r_obj['id']
        return None


    @staticmethod
    def sanitize_json_input(us_data):
        """
            Sanitizes data before going to Requests. This mostly
            handles cases where there are mixed-encoded objects
            where part of the object is ASCII/UTF-8 and the other
            part is Unicode.
        :param obj us_data: JSON-serializable Python object
        :returns: UTF-8 JSON object
        :rtype: JSON object
        """
        if not us_data:
            return None
        if not isinstance(us_data, dict) and not isinstance(us_data, list):
            return None
        return yaml.safe_load(
            json.dumps(us_data, ensure_ascii=True).encode('utf8'))

    @staticmethod
    def lowercase_headers(headers):
        # Convert headers from CaseInsensitiveDict to Dict
        return dict(headers.lower_items())
