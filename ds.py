#!/usr/bin/env python3

import yaml

from tabulate import tabulate
from utils import *
from models import KubeNode, Node


try:
    print()
    kube_api = get_kubernetes_api_object()
    kubernetes_nodes = kube_api.list_node().items
    kube_node_objs = []

    for node in kubernetes_nodes:
        addresses = []

        for address in node.status.addresses:
            addresses.append(address.address)

        kube_node = KubeNode(node.metadata.name, addresses, node.status.node_info.os_image, node.status.node_info.container_runtime_version,
                             node.status.node_info.kubelet_version, node.status.conditions[len(node.status.conditions)-1].type,
                             calculate_age(node.metadata.creation_timestamp),get_node_role(node.metadata.labels))
        kube_node_objs.append(kube_node)




    dsm = get_ds_api_object(yaml.safe_load(open('config.yaml', 'r')), kube_api)
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
                    add_details = [node.os, node.container_runtime, ds_host_detail['Agent Status'],ds_host_detail['AM'], ds_host_detail['WR'],ds_host_detail['DPI'], ds_host_detail['FW'], ds_host_detail['IM'], ds_host_detail['LI'], ds_host_detail['TUM']]
                    node_info = node_info + add_details

        if len(node_info) == 5:
            add_details = [node.os, node.container_runtime, "Not Installed", "NA", "NA", "NA", "NA", "NA", "NA", "NA"]
            node_info = node_info + add_details

        node_info_objs.append(node_info)
    dsm.end_session()
    print(tabulate(node_info_objs, headers=['NAME', 'STATUS', 'ROLE', 'AGE', 'VERSION', 'Operating System','Container Runtime','DS AGENT STATUS', 'AM', 'WR','DPI', 'FW', 'IM', 'LI', 'TUM']), end='\n\n')

except Exception as e:
    print(e)
    dsm.end_session()


