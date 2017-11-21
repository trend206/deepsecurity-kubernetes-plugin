from datetime import datetime
import pytz

from kubernetes import client, config

from models import KubeNode, Node


class KubeInterface():

    def __init__(self):
        config.load_kube_config()
        v1 = client.CoreV1Api()
        self.api = v1

    def get_nodes(self):
        kubernetes_nodes = self.api.list_node().items
        kube_node_objs = []

        for node in kubernetes_nodes:
            addresses = []

            for address in node.status.addresses:
                addresses.append(address.address)

            kube_node = KubeNode(node.metadata.name, addresses, node.status.node_info.os_image,
                                 node.status.node_info.container_runtime_version,
                                 node.status.node_info.kubelet_version,
                                 node.status.conditions[len(node.status.conditions) - 1].type,
                                 self._calculate_age(node.metadata.creation_timestamp), self._get_node_role(node.metadata.labels))
            kube_node_objs.append(kube_node)

        return kube_node_objs


    def _get_node_role(self, labels):
        role = "<none>"
        for label in labels:
            if 'node-role.kubernetes.io' in label:
                role = label.split("/")[1]
        return role

    def _calculate_age(self, born):
        age = (datetime.now().replace(tzinfo=pytz.utc) - born).days
        return 1 if age == 0 else age
