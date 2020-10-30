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
    resources.Credential
    ~~~~~~~~~~~~~~~~~~~~
    Ansible Tower Credential interface
"""

# Node properties and logger
from cloudify import ctx
# Lifecycle operation decorator
from cloudify.decorators import operation
# Base resource class
from cloudify_ansible_tower.resources.base import Resource
# API version
from cloudify_ansible_tower import utils
# Resources
from cloudify_ansible_tower.resources.organization import Organization
from cloudify_ansible_tower.resources.team import Team
from cloudify_ansible_tower.resources.user import User


class Credential(Resource):
    """
        Ansible Tower Credential interface
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
            'Credential',
            '/credentials',
            lookup=['id', 'url', 'name'],
            logger=logger,
            _ctx=_ctx)


class CredentialType(Resource):
    """
        Ansible Tower Credential Type interface
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
            'Credential Type',
            '/credential_types',
            lookup=['id', 'url', 'name'],
            logger=logger,
            _ctx=_ctx)


@operation(resumable=True)
def create(**_):
    """Uses an existing, or creates a new, Credential"""
    config = ctx.node.properties.get('resource_config')
    credential_type = config.get('credential_type')

    config['credential_type'] = \
        CredentialType().lookup_id(credential_type)

    # Get organization reference
    rel_org = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.contained_in_organization')
    if rel_org:
        config['organization'] = utils.get_resource_name(rel_org.target)
    elif config.get('organization'):
        config['organization'] = \
            Organization().lookup_id(config['organization'])

    # Get team reference
    rel_team = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.contained_in_team')
    if rel_team:
        config['team'] = utils.get_resource_name(rel_team.target)
    elif config.get('team'):
        config['team'] = Team().lookup_id(config['team'])

    # Get user reference
    rel_user = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.contained_in_user')
    if rel_user:
        config['user'] = utils.get_resource_name(rel_user.target)
    elif config.get('user'):
        config['user'] = User().lookup_id(config['user'])

    ctx.instance.runtime_properties['resource'] = \
        utils.task_resource_create(Credential(), config)
    ctx.instance.runtime_properties['resource_id'] = \
        ctx.instance.runtime_properties['resource'].get('id')


@operation(resumable=True)
def delete(**_):
    """Deletes a Credential"""
    utils.task_resource_delete(Credential())


@operation(resumable=True)
def create_type(**_):
    """Uses an existing, or creates a new, CredentialType"""
    ctx.instance.runtime_properties['resource'] = \
        utils.task_resource_create(
            CredentialType(),
            ctx.node.properties.get('resource_config'))
    ctx.instance.runtime_properties['resource_id'] = \
        ctx.instance.runtime_properties['resource'].get('id')


@operation(resumable=True)
def delete_type(**_):
    """Deletes a CredentialType"""
    utils.task_resource_delete(CredentialType())
