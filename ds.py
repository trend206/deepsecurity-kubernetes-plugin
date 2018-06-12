#!/usr/bin/env python3

import yaml
import urllib

from tabulate import tabulate
import click

from utils import Utils
from models import KubeNode, Node




@click.group()
def cli():
    """Welcome to the Deep Security kubectl plugin."""
    pass

@cli.command()
@click.argument('name', default="my-k8s-cluster")
def connector_create(name):
    """'name' creates a k8s connector in your dsm"""
    try:
        utils = Utils()
        utils.create_connector(name)
        utils.end_session()
    except urllib.error.URLError as urle:
        print("Unable to connect to the Deep Security Manager.")
        print("Please make sure the server is up.")
    except Exception as e:
        print("--------------------------------------------------")
        print(type(e))


@cli.command()
@click.argument('name')
@click.argument('node', default="all")
def assign_policy(name, node):
    try:
        utils = Utils()
        utils.assign_cluster_policy(name, node)
        utils.end_session()
    except urllib.error.URLError as urle:
        print("Unable to connect to the Deep Security Manager.")
        print("Please make sure the server is up.")
    except Exception as e:
        print("--------------------------------------------------")
        print(type(e))


@cli.command()
def connector_sync():
    """synchronizes new kubernetes nodes with connector"""
    try:
        utils = Utils()
        utils.sync_connector()
        utils.end_session()
    except urllib.error.URLError as urle:
        print("Unable to connect to the Deep Security Manager.")
        print("Please make sure the server is up.")
    except Exception as e:
        print("--------------------------------------------------")
        print(type(e))
        print(e)


@cli.command()
def status():
    """displays cluster security status"""
    try:
        print()
        utils = Utils()
        kube_node_objs = utils.kube_interface.get_nodes()
        ds_hosts = utils.dsm.host_retrieve_all()

        node_objs = []
        node_info_objs = []


        for node in kube_node_objs:
            node_info = [node.name, node.status, node.role, str(node.age) + "d", node.kubelet_version]
            exists = False
            for address in node.addresses:
                exists = [x for x in ds_hosts if x['displayName'] == address or x['name'] == address]
                if len(exists) > 0:
                    break

            if exists and exists[0]:
                ds_host_detail = utils.get_host_details(exists[0]['ID'])
                if ds_host_detail:
                    if ds_host_detail['Agent Status'] != 'Unmanaged (Unknown)':
                        add_details = [node.os, node.container_runtime, ds_host_detail['Agent Status'][:16], ds_host_detail['Policy'], ds_host_detail['AM'], ds_host_detail['WR'],ds_host_detail['DPI'], ds_host_detail['FW'], ds_host_detail['IM'], ds_host_detail['LI'], ds_host_detail['TUM']]
                    else:
                        add_details = [node.os, node.container_runtime, ds_host_detail['Agent Status'][:16], "NA", "NA", "NA", "NA", "NA", "NA","NA", "NA"]

                    node_info = node_info + add_details

            if len(node_info) == 5:
                add_details = [node.os, node.container_runtime, "Not Installed", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"]
                node_info = node_info + add_details

            node_info_objs.append(node_info)
        utils.end_session()
        print(tabulate(node_info_objs, headers=['NAME', 'STATUS', 'ROLE', 'AGE', 'VERSION', 'Operating System','Container Runtime','DS AGENT STATUS', 'Policy', 'AM', 'WR','DPI', 'FW', 'IM', 'LI', 'TUM']), end='\n\n')

    except urllib.error.URLError as urle:
        print("Unable to connect to the Deep Security Manager.")
        print("Please make sure the server is up.")
    except Exception as e:
        print("--------------------------------------------------")
        print(type(e))



if __name__ == '__main__':
    cli()