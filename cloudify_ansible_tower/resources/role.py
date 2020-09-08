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
    resources.Role
    ~~~~~~~~~~~~~~
    Ansible Tower Role interface
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
from cloudify_ansible_tower.resources.team import Team
from cloudify_ansible_tower.resources.user import User
from cloudify_ansible_tower.resources.project import Project
from cloudify_ansible_tower.resources.job_template import Job_Template


class Role(Resource):
    """
        Ansible Tower Role interface
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
            'Role',
            '/roles',
            lookup=['id', 'url', 'name'],
            logger=logger,
            _ctx=_ctx)

    def add(self, target, user, role):
        """
            Adds permission
        :param cloudify_ansible_tower.resources.user.User user: User
        :param str role: Permission to assign (Admin, Use, Update, Read)
        :param dict params: Parameters to be passed as-is to the API
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`
        """
        self.log.info('Adding {0}({1}) to {2}({3})'.format(
            user.name, user.resource_id, 
            target.name, target.resource_id))

        self.log.debug('Calling {0}'.format(target.lookup_role(role)['related'][user.name.lower() + 's']))

        # Make the request
        res = target.client.request(
            method='post', 
            url=target.lookup_role(role)['related'][user.name.lower() + 's'], 
            json=dict(id=user.resource_id))
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

    def remove(self, target, user, role):
        """
            Removes permission
        :param cloudify_ansible_tower.resources.user.User user: User
        :param str role: Permission to remove (Admin, Use, Update, Read)
        :param dict params: Parameters to be passed as-is to the API
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`
        """
        self.log.info('Removing {0}({1}) from {2}({3})'.format(
            user.name, user.resource_id, 
            target.name, target.resource_id))

        # Make the request
        res = target.client.request(
            method='post', 
            url=target.lookup_role(role)['related'][user.name.lower() + 's'], 
            json=dict(
                id=user.resource_id,
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


CLASS_MAP = {
  'cloudify.ansible_tower.nodes.JobTemplate': Job_Template,
  'cloudify.ansible_tower.nodes.Project': Project
}


@operation(resumable=True)
def add_user(role, **_):
    Role(_ctx=ctx.source).add(
        CLASS_MAP[ctx.source.node.type](_ctx=ctx.source),
        User(_ctx=ctx.target), role)

@operation(resumable=True)
def remove_user(role, **_):
    Role(_ctx=ctx.source).remove(
        CLASS_MAP[ctx.source.node.type](_ctx=ctx.source),
        User(_ctx=ctx.target), role)


@operation(resumable=True)
def add_team(role, **_):
    Role(_ctx=ctx.source).add(
        CLASS_MAP[ctx.source.node.type](_ctx=ctx.source),
        Team(_ctx=ctx.target), role)


@operation(resumable=True)
def remove_team(role, **_):
    Role(_ctx=ctx.source).remove(
        CLASS_MAP[ctx.source.node.type](_ctx=ctx.source),
        Team(_ctx=ctx.target), role)
