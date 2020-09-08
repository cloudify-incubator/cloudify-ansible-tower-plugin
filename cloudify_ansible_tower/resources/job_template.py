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
    resources.Job_Template
    ~~~~~~~~~~~~~~~~~~~~~~
    Ansible Tower Job_Template interface
"""

from requests import codes as http_codes
# Node properties and logger
from cloudify import ctx
# Exceptions
from cloudify.exceptions import NonRecoverableError, RecoverableError
# Lifecycle operation decorator
from cloudify.decorators import operation
# API version
from cloudify_ansible_tower import utils
# Base resource class
from cloudify_ansible_tower.resources.base import Resource
# Resources
from cloudify_ansible_tower.resources.credential import Credential
from cloudify_ansible_tower.resources.project import Project
from cloudify_ansible_tower.resources.inventory import Inventory


class Job_Template(Resource):
    """
        Ansible Tower Job_Template interface
    .. warning::
        This interface should only be instantiated from
        within a Cloudify Lifecycle Operation
    :param string api_version: API version to use for all requests
    :param `logging.Logger` logger:
        Parent logger for the class to use. Defaults to `ctx.logger`
    """
    def __init__(self, logger=None, _ctx=ctx):
        Resource.__init__(
            self,
            'Job_Template',
            '/job_templates',
            lookup=['id', 'url', 'name'],
            logger=logger,
            _ctx=_ctx)

    def add_credential(self, credential):
        """
            Adds credentials
        :param cloudify_ansible_tower.resources.credential.Credential credential: Credential
        :param str credential: Credential
        :param dict params: Parameters to be passed as-is to the API
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`
        """
        self.log.info('Adding {0}({1}) to {2}({3})'.format(
            credential.name, credential.resource_id, 
            self.name, self.resource_id))

        # Make the request
        res = self.client.request(
            method='post', 
            url=self.resource_url + 'credentials/',
            json=dict(id=credential.resource_id))
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        headers = self.lowercase_headers(res.headers)
        # Check the response
        # If API sent a 400, we're sending bad data
        if res.status_code == http_codes.bad_request:
            self.log.info('BAD REQUEST: response: {}'.format(res.content))
            raise NonRecoverableError(
                '{0} BAD REQUEST'.format(target.name))
        # All other errors will be treated as recoverable
        if res.status_code != http_codes.no_content:
            raise RecoverableError(
                'Expected HTTP status code {0}, recieved {1}'
                .format(http_codes.no_content, res.status_code))

    def remove_credential(self, credential):
        """
            Removes credentials
        :param cloudify_ansible_tower.resources.credential.Credential credential: Credential
        :param str credential: Credential
        :param dict params: Parameters to be passed as-is to the API
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`
        """
        self.log.info('Removing {0}({1}) from {2}({3})'.format(
            credential.name, credential.resource_id, 
            self.name, self.resource_id))

        # Make the request
        res = self.client.request(
            method='post', 
            url=self.resource_url + 'credentials/',
            json=dict(
              id=credential.resource_id,
              disassociate=True))
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        headers = self.lowercase_headers(res.headers)
        # Check the response
        # If API sent a 400, we're sending bad data
        if res.status_code == http_codes.bad_request:
            self.log.info('BAD REQUEST: response: {}'.format(res.content))
            raise NonRecoverableError(
                '{0} BAD REQUEST'.format(target.name))
        # All other errors will be treated as recoverable
        if res.status_code != http_codes.no_content:
            raise RecoverableError(
                'Expected HTTP status code {0}, recieved {1}'
                .format(http_codes.no_content, res.status_code))

    def lookup_role(self, name):
        """
            Find a resource
        :param string name: Name/ID of the existing resource
        :returns: Resource
        :rtype: dict
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`,
        """
        _lookup = ['id', 'url', 'name']
        self.log.info('Retrieving roles for {0}'.format(self.name))
        # Make the request
        res = self.client.request(
            method='get', 
            url=self.resource_url + 'object_roles/')
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        headers = self.lowercase_headers(res.headers)
        # Check the response
        # HTTP 200 (OK) - The resource already exists
        if res.status_code != http_codes.ok:
            raise RecoverableError(
                'Expected HTTP status code {0}, recieved {1}'
                .format(http_codes.ok, res.status_code))
        # Get list of resources
        obj = None
        for r_obj in res.json().get('results', list()):
            for lookup in _lookup:
                if name == r_obj.get(lookup):
                    return r_obj
        return None


@operation(resumable=True)
def create(**_):
    """Uses an existing, or creates a new, Job_Template"""
    config = ctx.node.properties.get('resource_config')

    # Get project reference
    rel_project = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.contained_in_project')
    if rel_project:
        config['project'] = utils.get_resource_name(rel_project.target)
    elif config.get('project'):
        config['project'] = \
            Project().lookup_id(config['project'])

    # Get inventory reference
    rel_inventory = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.connected_to_inventory')
    if rel_inventory:
        config['inventory'] = utils.get_resource_name(rel_inventory.target)
    elif config.get('inventory'):
        config['inventory'] = \
            Inventory().lookup_id(config['inventory'])

    ctx.instance.runtime_properties['resource'] = \
        utils.task_resource_create(Job_Template(), config)
    ctx.instance.runtime_properties['resource_id'] = \
        ctx.instance.runtime_properties['resource'].get('id')


@operation(resumable=True)
def delete(**_):
    """Deletes a Job_Template"""
    utils.task_resource_delete(Job_Template())

@operation(resumable=True)
def link_credential(**_):
    Job_Template(_ctx=ctx.source).add_credential(
        Credential(_ctx=ctx.target))

@operation(resumable=True)
def unlink_credential(**_):
    Job_Template(_ctx=ctx.source).remove_credential(
        Credential(_ctx=ctx.target))
