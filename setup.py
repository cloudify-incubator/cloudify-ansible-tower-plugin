# #######
# Copyright (c) 2020 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
'''Ansible Tower / AWX plugin for Cloudify package config'''

from setuptools import setup

setup(
    name='cloudify-ansible-tower-plugin',
    version='1.0.0',
    license='LICENSE',
    packages=[
        'cloudify_ansible_tower',
        'cloudify_ansible_tower.resources'
    ],
    description='Cloudify plugin for Ansible Tower / AWX',
    install_requires=[
        'cloudify-common>=4.5',
        'requests~=2.23.0'
    ]
)
