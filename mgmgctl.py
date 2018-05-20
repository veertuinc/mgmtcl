#!/usr/local/bin/python

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



import os
from collections import OrderedDict
import lib.click as click

host = None


def set_host_variable():
    global host
    host_path = os.path.join(os.path.dirname(__file__), 'host')
    if not os.path.exists(host_path):
        click.echo("Please define a host")
        exit(-1)
    with open(host_path) as f:
        host = f.read().rstrip()
    validate_host(host)


def validate_host(host_str):
    url_regex = 'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    import re
    if not re.match(url_regex, host_str):
        click.echo("Host string should be a valid url")
        exit(-1)



@click.group()
def main():
    pass


@main.group()
def vm():
    set_host_variable()


@vm.command(name='list')
def list_vms():
    from management_api import ManagementApi
    mgmt_api = ManagementApi(host)
    list_of_vms = mgmt_api.list()
    click.echo("\nvms:\n")
    from formatter import Formatter
    formatter = Formatter()
    click.echo(formatter.format_list_of_dicts(list_of_vms))
    click.echo("\n")


@vm.command(name='start')
@click.argument('template-id', type=click.STRING)
@click.option('--tag', type=click.STRING, default=None)
@click.option('--count', type=click.INT, default=1)
@click.option('--node', type=click.STRING, default=None)
@click.option('--name', type=click.STRING, default=None)
@click.option('--script-file', type=click.STRING, default=None)
def start_vm(template_id, tag, count, node, name, script_file):
    from management_api import ManagementApi
    from management_api import NotFoundException
    mgmt_api = ManagementApi(host)
    new_ids = None
    try:
        if script_file != None and not os.path.exists(script_file):
            click.echo("File %s does not exist" % script_file)
            exit(-1)
        new_ids = mgmt_api.start_vm(template_id, count, tag=tag, node=node, name=name, script_file=script_file)
    except NotFoundException:
        template_id_from_list = mgmt_api.search_template_by_name(template_id)
        if template_id_from_list:
            new_ids = mgmt_api.start_vm(template_id_from_list, count, tag=tag, node=node, name=name)
        else:
            click.echo("Template not found")
            exit(-1)
    if new_ids:
        click.echo("\nvms created")
        vms_created = []
        for new_id in new_ids:
            vm_info = mgmt_api.show_vm(new_id)
            info_to_show = {'id': new_id, 'state': vm_info.get('instance_state')}
            vms_created.append(info_to_show)
        from formatter import Formatter
        formatter = Formatter()
        click.echo(formatter.format_list_of_dicts(vms_created))
    else:
        click.echo("\ncreate failed")


@vm.command(name='show')
@click.argument('vm-id', type=click.STRING)
def show_vm(vm_id):
    from management_api import ManagementApi
    from management_api import NotFoundException
    mgmt_api = ManagementApi(host)
    try:
        vm = mgmt_api.show_vm(vm_id)
    except NotFoundException:
        click.echo("vm not found")
        exit(-1)
    click.echo("\nshowing vm %s\n" % vm_id)
    from formatter import Formatter
    formatter = Formatter()
    click.echo(formatter.format_dict(vm))


@vm.command(name='terminate')
@click.argument('vm-id', type=click.STRING)
def terminate_vm(vm_id):
    from management_api import ManagementApi
    mgmt_api = ManagementApi(host)
    result = mgmt_api.terminate_vm(vm_id)
    if result:
        click.echo("\nterminating...\n")
        ctx = click.get_current_context()
        ctx.invoke(show_vm, vm_id=vm_id)
    else:
        click.echo("\nunable to terminate %s\n" % vm_id)


@main.group()
def node():
    set_host_variable()


@node.command(name='list')
def list_nodes():
    from management_api import ManagementApi
    mgmt_api = ManagementApi(host)

    result = mgmt_api.list_nodes()
    from formatter import Formatter
    formatter = Formatter()
    click.echo(formatter.format_list_of_dicts(result))


@node.command(name='show')
@click.argument("node-id", type=click.STRING)
def show_node(node_id):
    from management_api import ManagementApi
    from management_api import NotFoundException
    mgmt_api = ManagementApi(host)
    try:
        result = mgmt_api.show_node(node_id)
    except NotFoundException:
        click.echo("no such node")
        exit(-1)
    from formatter import Formatter
    formatter = Formatter()
    click.echo(formatter.format_list_of_dicts(result))


@main.group()
def template():
    set_host_variable()


@template.command(name='list')
def list_templates():
    from management_api import ManagementApi
    mgmt_api = ManagementApi(host)

    result = mgmt_api.list_registry()
    from formatter import Formatter
    formatter = Formatter()
    click.echo(formatter.format_list_of_dicts(result))


@template.command(name='show')
@click.argument('vm-id', type=click.STRING)
def show_template(vm_id):
    from management_api import ManagementApi
    from management_api import NotFoundException
    mgmt_api = ManagementApi(host)
    vm = {}
    try:
        vm = mgmt_api.show_registry(vm_id)
    except NotFoundException:
        template_id_from_list = mgmt_api.search_template_by_name(vm_id)
        if template_id_from_list:
            vm = mgmt_api.show_registry(template_id_from_list)
        else:
            click.echo('Template not found')
            exit(-1)

    versions = vm.pop('versions', [])
    vm_dict = OrderedDict([('id', vm.get('id')), ('name', vm.get('name'))])
    formatted_versions = []
    for version_dict in versions:
        number = version_dict.get('number')
        tag = version_dict.get('tag', '-')
        formatted_versions.append(OrderedDict([('number', number), ('tag', tag)]))
    vm_dict['versions'] = formatted_versions
    from formatter import Formatter
    formatter = Formatter()
    click.echo(formatter.format_dict(vm_dict))


@main.group()
def host():
    pass


@host.command(name='set', help='set the controller\'s connection string')
@click.argument('host-string')
def set_host(host_string):
    validate_host(host_string)
    with open(os.path.join(os.path.dirname(__file__), 'host'), 'w') as f:
        f.write(host_string)
    click.echo("set host to %s" % host_string)


@host.command(name='show', help='show the host currently set')
def show_host():
    set_host_variable()
    click.echo(host)


def main_wrapper():
    main()


if __name__ == '__main__':
    main_wrapper()
