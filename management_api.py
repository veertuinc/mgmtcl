# Copyright 2017 Veertu Inc
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided
# that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of
# conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials provided
# with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to
# endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
from collections import OrderedDict

import requests

class ManagementApi(object):

    def __init__(self, base_url):
        self.base_url = base_url
        self.vm_resource = "api/v1/vm"
        self.node_resource = "api/v1/node"
        self.registry_vm_resource = "api/v1/registry/vm"

    def list(self):
        url = "%s/%s" % (self.base_url, self.vm_resource)
        response = requests.get(url)
        response.raise_for_status()
        response_dict = json.loads(response.content)
        vms_list_to_return = []
        if response_dict.get('status') == "OK":
            vms_dicts = response_dict.get("body", [])
            for vm_status in vms_dicts:
                # print vm_status
                vm_dict = OrderedDict()
                vm_dict['id'] = vm_status.get('instance_id')
                # vm_dict.update(vm_status.get('vm'))

                vm_dict['source_vm'] = vm_status.get('vm', {}).get("vmid")
                vm_dict['instance_state'] = vm_status.get('vm', {}).get("instance_state")
                vm_dict['vnc_string'] = vm_status.get('vm', {}).get("vminfo", {}).get("vnc_connection_string")
                if vm_status:
                    vms_list_to_return.append(vm_dict)
        return vms_list_to_return

    def start_vm(self, vm_id, count, tag=None, node=None):
        url = "%s/%s" % (self.base_url, self.vm_resource)
        args = {"vmid": vm_id, "count": count}
        if tag:
            args['tag'] = tag
        if node:
            args['node_id'] = node
        response = requests.post(url, json=args)
        response.raise_for_status()
        response_dict = json.loads(response.content)
        if response_dict.get('status') == "OK":
            return response_dict.get("body")
        if response_dict.get('message') == 'VM not in the registry':
            raise NotFoundException()
        return None

    def search_template_by_name(self, vm_name):
        vms = self.list_registry()
        for vm in vms:
            if vm.get('name') == vm_name:
                return vm.get('id')
        return None

    def show_vm(self, vm_id):
        url = "%s/%s?id=%s" % (self.base_url, self.vm_resource, vm_id)
        response = requests.get(url)
        response.raise_for_status()
        response_dict = json.loads(response.content)
        if response_dict.get('status') == "OK":
            return response_dict.get('body')
        if response_dict.get('message') == 'Not found':
            raise NotFoundException()
        return {}

    def terminate_vm(self, vm_id):
        url = "%s/%s" % (self.base_url, self.vm_resource)
        response = requests.delete(url, json={"id": vm_id})
        response.raise_for_status()
        response_dict = json.loads(response.content)
        if response_dict.get('status') == "OK":
            return response_dict
        return {}

    def list_nodes(self):
        url = "%s/%s" % (self.base_url, self.node_resource)
        response = requests.get(url)
        response.raise_for_status()
        response_dict = json.loads(response.content)
        if response_dict.get('status') == "OK":
            return response_dict.get('body')
        return []

    def show_node(self, node_id):
        url = "%s/%s?id=%s" % (self.base_url, self.node_resource, node_id)
        response = requests.get(url)
        response.raise_for_status()
        response_dict = json.loads(response.content)
        if response_dict.get('status') == "OK":
            return response_dict.get("body")
        if response_dict.get('message') == 'Not found':
            raise NotFoundException()
        return []

    def list_registry(self):
        url = "%s/%s" % (self.base_url, self.registry_vm_resource)
        response = requests.get(url)
        response.raise_for_status()
        response_dict = json.loads(response.content)
        if response_dict.get('status') == "OK":
            return response_dict.get('body')
        return []

    def show_registry(self, vm_id):
        url = "%s/%s?id=%s" % (self.base_url, self.registry_vm_resource, vm_id)
        response = requests.get(url)
        response.raise_for_status()
        response_dict = json.loads(response.content)
        if response_dict.get('status') == "OK":
            return response_dict.get('body')
        if response_dict.get('message') == 'Not found':
            raise NotFoundException()
        return {}


class NotFoundException(Exception):
    pass

