#!/usr/bin/env python3

import yaml
import urllib

from tabulate import tabulate
import click

from utils import *
from models import KubeNode, Node


dsm = get_ds_api_object(yaml.safe_load(open('config.yaml', 'r')), kube_interface.api)

@click.group()
def cli():
    pass

@cli.command()
@click.option('/create', default=False, help='creates a Kubernetes connector in DSM.')
@click.option('/clear', is_flag=True, help="removes all k8s nodes from connectors")
#@click.option('--exists', is_flag=True, help="checks to see if any Kubernetes connectors exist")
def connector(create, clear):
    dsm = get_ds_api_object(yaml.safe_load(open('config.yaml', 'r')), kube_interface.api)
    if clear:
        ids = dshosts_that_map_to_kubenodes(dsm)
        dsm.host_move_to_hosts_group(ids, 0)
    elif create:
        print(create_connector(dsm, create))

    dsm.end_session()

@cli.command()
def nodes():
    try:
        print()
        kube_node_objs = kube_interface.get_nodes()
        ds_hosts = dsm.host_retrieve_all()

        node_objs = []
        node_info_objs = []


        for node in kube_node_objs:
            node_info = [node.name, node.status, node.role, str(node.age) + "d", node.kubelet_version]
            exists = False
            for address in node.addresses:
                exists = [x for x in ds_hosts if x['displayName'] == address]

                if exists and exists[0]:
                    ds_host_detail = get_host_details(dsm, exists[0]['ID'])
                    if ds_host_detail:
                        node_obj = Node(node_info[0], node_info[1], node_info[2], node_info[3], node_info[4], ds_host_detail['Agent Status'],
                                        ds_host_detail['AM'], ds_host_detail['WR'], ds_host_detail['DPI'], ds_host_detail['FW'], ds_host_detail['IM'], ds_host_detail['LI'], ds_host_detail['TUM'])
                        node_objs.append(node_obj)
                        add_details = [node.os, node.container_runtime, ds_host_detail['Agent Status'][:16],ds_host_detail['AM'], ds_host_detail['WR'],ds_host_detail['DPI'], ds_host_detail['FW'], ds_host_detail['IM'], ds_host_detail['LI'], ds_host_detail['TUM']]
                        node_info = node_info + add_details

            if len(node_info) == 5:
                add_details = [node.os, node.container_runtime, "Not Installed", "NA", "NA", "NA", "NA", "NA", "NA", "NA"]
                node_info = node_info + add_details

            node_info_objs.append(node_info)
        dsm.end_session()
        print(tabulate(node_info_objs, headers=['NAME', 'STATUS', 'ROLE', 'AGE', 'VERSION', 'Operating System','Container Runtime','DS AGENT STATUS', 'AM', 'WR','DPI', 'FW', 'IM', 'LI', 'TUM']), end='\n\n')

    except urllib.error.URLError as urle:
        print("Unable to connect to the Deep Security Manager.")
        print("Please make sure the server is up.")
    except Exception as e:
        print("--------------------------------------------------")
        print(type(e))
        dsm.end_session()


if __name__ == '__main__':
    cli()