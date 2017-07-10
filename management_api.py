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

    def start_vm(self, vm_id, count, tag=None):
        url = "%s/%s" % (self.base_url, self.vm_resource)
        args = {"vmid": vm_id, "count": count}
        if tag:
            args['tag'] = tag
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

