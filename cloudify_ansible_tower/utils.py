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
    Utils
    ~~~~~
    Ansible Tower plugin for Cloudify helper utilities
"""

# Py3 Compatibility

from logging import DEBUG
from collections import namedtuple

from cloudify import ctx

APICredentials = namedtuple(
    'APICredentials',
    ['endpoint', 'endpoint_verify', 'access_token'])


def create_child_logger(name,
                        plogger=None,
                        level=DEBUG):
    """
        Creates a child logger and sets the log level
    .. note::
           If `plogger` is not specified, this method will default
           to using `ctx.logger` as the parent logger.
    Example::
        # Import
        from cloudify_ansible_tower import utils
        # Get a child Cloudify logger for a subroutine
        log = utils.create_child_logger('myclass.myfunc')
        # Use the logger as normal
        log.debug('Child logger!')
    :param string name: Name of the child logger
    :param `logging.Logger` plogger: Parent logger
    :param int level: Log level
    :returns: A configured child logger
    :rtype: :class:`logging.Logger`
    """
    plogger = plogger or ctx.logger
    log = plogger.getChild(name)
    log.setLevel(level)
    return log


def dict_update(orig, updates):
    """Recursively merges two objects"""
    for key, val in updates.items():
        if isinstance(val, Mapping):
            orig[key] = dict_update(orig.get(key, {}), val)
        else:
            orig[key] = updates[key]
    return orig


def get_credentials(_ctx=ctx):
    """
        Gets any Tower API access information from the
        current node properties or a provider context
        file created during manager bootstrapping.
    :returns: API credentials and access information
    :rtype: :class:`cloudify_ansible_tower.utils.APICredentials`
    """
    cred_keys = ['endpoint', 'endpoint_verify', 'access_token']
    props = _ctx.node.properties.get('client_config')
    properties = {k: props[k] for k in cred_keys if props.get(k)}
    return APICredentials(**properties)


def runtime_properties_cleanup(ctx):
    # cleanup runtime properties
    for key in list(ctx.instance.runtime_properties.keys()):
        del ctx.instance.runtime_properties[key]


def get_resource_name(_ctx=ctx):
    """
        Finds a resource's name
    :returns: The resource's name or None
    :rtype: string
    """
    return _ctx.instance.runtime_properties.get('resource_id') or \
        _ctx.node.properties.get('resource_id')


def task_resource_create(resource, params,
                         use_external=None, _ctx=ctx):
    """
        Creates a new API resource.

    :param `cloudify_ansible_tower.resources.base.Resource` resource:
        The resource interface object to perform resource
        operations on
    :param dict params: Resource parameters to be passed as-is to the API
    :param string name: The resource name, as identified in the API.
    :raises: :exc:`cloudify.exceptions.RecoverableError`,
             :exc:`cloudify.exceptions.NonRecoverableError`,
             :exc:`requests.RequestException`
    """
    # Get use_external_resource boolean
    if use_external is None:
        use_external = _ctx.node.properties.get('use_external_resource')
    # Check for existing resources
    if use_external:
        return resource.get()
    # Create a new resource
    return resource.create(params)


def task_resource_delete(resource, _ctx=ctx):
    """
        Deletes an existing API resource.

    :param `cloudify_ansible_tower.resources.base.Resource` resource:
        The resource interface object to perform resource
        operations on
    :raises: :exc:`cloudify.exceptions.RecoverableError`,
             :exc:`cloudify.exceptions.NonRecoverableError`,
             :exc:`requests.RequestException`
    """
    # Check for existing resources
    if _ctx.node.properties.get('use_external_resource'):
        return resource.get()
    # Delete the resource
    if resource.exists():
        resource.delete()
    else:
        _ctx.logger.info("Resource doesn't exist")
    runtime_properties_cleanup(_ctx)


def get_relationship_by_type(rels, rel_type):
    """
        Finds a relationship by a relationship type
    Example::
        # Import
        from cloudify import ctx
        from cloudify_ansible_tower import utils
        # Find a specific relationship
        rel = utils.get_relationship_by_type(
            ctx.instance.relationships,
            'cloudify.ansible_tower.relationships.a_custom_relationship')
    :param list<`cloudify.context.RelationshipContext`> rels: \
        List of Cloudify instance relationships
    :param string rel_type: Relationship type
    :returns: Relationship object or None
    :rtype: :class:`cloudify.context.RelationshipContext`
    """
    if not isinstance(rels, list):
        return None
    for rel in rels:
        if rel_type in rel.type_hierarchy:
            return rel
    return None


def get_relationships_by_type(rels, rel_type):
    """
        Finds relationships by a relationship type
    Example::
        # Import
        from cloudify import ctx
        from cloudify_ansible_tower import utils
        # Find specific relationships
        rels = utils.get_relationships_by_type(
            ctx.instance.relationships,
            'cloudify.ansible_tower.relationships.a_custom_relationship')
    :param list<`cloudify.context.RelationshipContext`> rels: \
        List of Cloudify instance relationships
    :param string rel_type: Relationship type
    :returns: List of relationship objects
    :rtype: list of :class:`cloudify.context.RelationshipContext`
    """
    ret = list()
    if not isinstance(rels, list):
        return ret
    for rel in rels:
        if rel_type in rel.type_hierarchy:
            ret.append(rel)
    return ret
