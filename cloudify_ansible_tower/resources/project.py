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
    resources.Project
    ~~~~~~~~~~~~~~~~~
    Ansible Tower Project interface
"""

# Node properties and logger
from cloudify import ctx
# Lifecycle operation decorator
from cloudify.decorators import operation
# API version
from cloudify_ansible_tower import utils
# Base resource class
from cloudify_ansible_tower.resources.base import Resource
# Resources
from cloudify_ansible_tower.resources.organization import Organization


class Project(Resource):
    """
        Ansible Tower Project interface
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
            'Project',
            '/projects',
            lookup=['id', 'url', 'name'],
            logger=logger,
            _ctx=_ctx)


@operation(resumable=True)
def create(**_):
    """Uses an existing, or creates a new, Project"""
    config = ctx.node.properties.get('resource_config')

    # Get organization reference
    rel_org = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.contained_in_organization')
    if rel_org:
        config['organization'] = utils.get_resource_name(rel_org.target)
    elif config.get('organization'):
        config['organization'] = \
            Organization().lookup_id(config['organization'])

    ctx.instance.runtime_properties['resource'] = \
        utils.task_resource_create(Project(), config)
    ctx.instance.runtime_properties['resource_id'] = \
        ctx.instance.runtime_properties['resource'].get('id')


@operation(resumable=True)
def delete(**_):
    """Deletes a Project"""
    utils.task_resource_delete(Project())
