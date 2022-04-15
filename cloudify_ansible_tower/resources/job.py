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
    resources.Job
    ~~~~~~~~~~~~~
    Ansible Tower Job interface
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
from cloudify_ansible_tower.resources.job_template import JobTemplate


class Job(Resource):
    """
        Ansible Tower Job interface
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
            'Job',
            '/jobs',
            lookup=['id', 'url', 'name'],
            logger=logger,
            _ctx=_ctx)


@operation(resumable=True)
def create(**_):
    """Uses an existing, or creates a new, Job"""
    config = ctx.node.properties.get('resource_config')

    # Get project reference
    rel_template = utils.get_relationship_by_type(
        ctx.instance.relationships,
        'cloudify.ansible_tower.relationships.job_contained_in_job_template')
    if rel_template:
        job_template_id = utils.get_resource_name(rel_template.target)
    elif config.get('job_template'):
        job_template_id = \
            JobTemplate().lookup_id(config['job_template'])

    resource = JobTemplate(_id=job_template_id).launch()

    ctx.instance.runtime_properties['resource'] = resource
    ctx.instance.runtime_properties['resource_id'] = resource.get('job')


@operation(resumable=True)
def delete(**_):
    """Deletes a Job"""
    job_object = Job()
    job_object.resource_id = ctx.instance.runtime_properties['resource_id']
    utils.task_resource_delete(job_object)
