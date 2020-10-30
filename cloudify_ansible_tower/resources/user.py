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
    resources.User
    ~~~~~~~~~~~~~~
    Ansible Tower User interface
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

class User(Resource):
    """
        Ansible Tower User interface
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
            'User',
            '/users',
            lookup=['id', 'url', 'username'],
            logger=logger,
            _ctx=_ctx)


@operation(resumable=True)
def create(**_):
    """Uses an existing, or creates a new, User"""
    ctx.instance.runtime_properties['resource'] = \
        utils.task_resource_create(
            User(),
            ctx.node.properties.get('resource_config'))
    ctx.instance.runtime_properties['resource_id'] = \
        ctx.instance.runtime_properties['resource'].get('id')

    # Get team reference
    rel_team = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.connected_to_team')
    if rel_team:
        Team(_ctx=rel_team.target).add_user(User())

    # Get org reference
    rel_org = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.contained_in_organization')
    if rel_org:
        Organization(_ctx=rel_org.target).add_user(User())


@operation(resumable=True)
def delete(**_):
    """Deletes a User"""
    # Get team reference
    rel_team = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.connected_to_team')
    if rel_team:
        Team(_ctx=rel_team.target).remove_user(User())

    # Get org reference
    rel_org = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.contained_in_organization')
    if rel_org:
        Organization(_ctx=rel_org.target).remove_user(User())

    utils.task_resource_delete(User())
