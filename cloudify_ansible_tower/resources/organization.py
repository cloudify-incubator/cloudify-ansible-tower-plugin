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
# pylint: disable=no-member
"""
    resources.Organization
    ~~~~~~~~~~~~~~~~~~~~~~
    Ansible Tower Organization interface
"""

from requests import codes as http_codes
# Node properties and logger
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError, RecoverableError
# Lifecycle operation decorator
from cloudify.decorators import operation
# Base resource class
from cloudify_ansible_tower.resources.base import Resource
# API version
from cloudify_ansible_tower import utils


class Organization(Resource):
    """
        Ansible Tower Organization interface
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
            'Organization',
            '/organizations',
            lookup=['id', 'url', 'name'],
            logger=logger,
            _ctx=_ctx)

    def add_user(self, user):
        """
            Adds a User to an Organization
        :param cloudify_ansible_tower.resources.user.User user: User
        :param dict params: Parameters to be passed as-is to the API
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`
        """
        self.log.info('Adding User({0}) to Organization({1})'.format(
            user.resource_id, self.resource_id))

        # Make the request
        res = self.client.request(
            method='post',
            url=self.resource_url + 'users/',
            json=dict(id=user.resource_id))
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        # Check the response
        # If API sent a 400, we're sending bad data
        if res.status_code == http_codes.bad_request:
            self.log.info('BAD REQUEST: response: {}'.format(res.content))
            raise NonRecoverableError(
                '{0} BAD REQUEST'.format(self.name))
        # All other errors will be treated as recoverable
        if res.status_code != http_codes.no_content:
            raise RecoverableError(
                'Expected HTTP status code {0}, recieved {1}'
                .format(http_codes.no_content, res.status_code))

    def remove_user(self, user):
        """
            Removes a User from an Organization
        :param cloudify_ansible_tower.resources.user.User user: User
        :param dict params: Parameters to be passed as-is to the API
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`
        """
        self.log.info('Removing User({0}) from Organization({1})'.format(
            user.resource_id, self.resource_id))

        # Make the request
        res = self.client.request(
            method='post',
            url=self.resource_url + 'users/',
            json=dict(
                id=user.resource_id,
                disassociate=True))
        self.log.debug('headers: {0}'.format(dict(res.headers)))
        # Check the response
        # If API sent a 400, we're sending bad data
        if res.status_code == http_codes.bad_request:
            self.log.info('BAD REQUEST: response: {}'.format(res.content))
            raise NonRecoverableError(
                '{0} BAD REQUEST'.format(self.name))
        # All other errors will be treated as recoverable
        if res.status_code != http_codes.no_content:
            raise RecoverableError(
                'Expected HTTP status code {0}, recieved {1}'
                .format(http_codes.no_content, res.status_code))


@operation(resumable=True)
def create(**_):
    """Uses an existing, or creates a new, Organization"""
    ctx.instance.runtime_properties['resource'] = \
        utils.task_resource_create(
            Organization(),
            ctx.node.properties.get('resource_config'))
    ctx.instance.runtime_properties['resource_id'] = \
        ctx.instance.runtime_properties['resource'].get('id')


@operation(resumable=True)
def delete(**_):
    """Deletes a Organization"""
    utils.task_resource_delete(Organization())
