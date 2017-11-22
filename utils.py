import sys
import base64
import json
import pytz
import yaml
from datetime import datetime
from dsp3.models.manager import Manager
from kubernetes import client, config

from kube_interface import KubeInterface

from models import KubeNode, Node

kube_interface = KubeInterface()

class Utils():

    def __init__(self):
        self.kube_interface = KubeInterface()
        self.dsm = self.get_ds_api_object(yaml.safe_load(open('config.yaml', 'r')))

    def get_host_details(self, host_id):
        status = {}
        host = self.dsm.host_status(host_id)

        status['Agent Status'] = host['overallStatus']
        status['AM'] = "Off" if "Off" in host['overallAntiMalwareStatus'] else "On"
        status['WR'] = "Off" if "Off" in host['overallWebReputationStatus'] else "On"
        status['DPI'] = "Off" if "Off" in host['overallDpiStatus'] else "On"
        status['FW'] = "Off" if "Off" in host['overallFirewallStatus'] else "On"
        status['IM'] = "Off" if "Off" in host['overallIntegrityMonitoringStatus'] else "On"
        status['LI'] = "Off" if "Off" in host['overallLogInspectionStatus'] else "On"
        trusted_update_mode = json.loads(self.dsm.get_trusted_update_mode(host_id))
        status['TUM'] = "Off" if "off" in trusted_update_mode['DescribeTrustedUpdateModeResponse']['state'] else "On"
        return status


    def calculate_age(self, born):
        age = (datetime.now().replace(tzinfo=pytz.utc) - born).days
        return 1 if age == 0 else age

    def get_node_role(self, labels):
        role = "<none>"
        for label in labels:
            if 'node-role.kubernetes.io' in label:
                role = label.split("/")[1]
        return role

    def get_ds_password(self, kube_api):
        secrets = kube_api.list_secret_for_all_namespaces().items
        password = None
        for secret in secrets:
            if secret.metadata.name == 'deepsecurity':
                password = base64.b64decode(secret.data['password']).decode('utf-8')

        return password


    def get_ds_api_object(self, config):
        dsm = None
        using_dsas = config['using_dsas']
        username = config['ds_username']
        password = self.get_ds_password(self.kube_interface.api)
        if password == None:
            print("Deep Security password not found as Kubernetes Secret")
            sys.exit()

        host = config['ds_host']
        port = config['ds_port']
        if using_dsas:
            tenant = config['dsas_tenant']
            dsm = Manager(username=username, password=password, tenant=tenant)
        else:
            dsm = Manager(username=username, password=password, host=host, port=port)

        return dsm


    def _does_connector_exist(self, name):
        connector_exists = False
        id = None
        host_groups = self.dsm.host_group_retrieve_all()
        exists = [x for x in host_groups if x['name'] == name]
        if len(exists) > 0:
            connector_exists = True
            id = exists[0]['ID']

        return (connector_exists , id)

    def dshosts_that_map_to_kubenodes(self):
        ids = []
        ds_hosts = self.dsm.host_retrieve_all()
        kube_nodes = kube_interface.get_nodes()

        for node in kube_nodes:
            for address in node.addresses:
                exists = [x for x in ds_hosts if x['displayName'] == address]

                if exists and exists[0]:
                    ids.append(exists[0]['ID'])

        return ids

    def sync_connector(self):
        group_id = self.get_master_group_id()
        if group_id:
            ids = self.dshosts_that_map_to_kubenodes()
            self.dsm.host_move_to_hosts_group(ids, group_id)
            print("%s connector sync complete" % self.get_connector_name(group_id))
        else:
            print("Connector does not exist. Please run kubectl plugin ds connector_create 'name'")


    def get_connector_name(self, group_id):
        return self.dsm.host_group_retrieve_by_id(group_id)['name']

    def get_master_group_id(self):
        group_id = None
        kube_nodes = kube_interface.get_nodes()
        ds_hosts = self.dsm.host_retrieve_all()
        master = None

        for node in kube_nodes:
            if node.role == 'master':
                master = node
                for address in node.addresses:
                    exists = [x for x in ds_hosts if x['displayName'] == address or x['name'] == address]
                    if exists and exists[0]:
                        group_id = exists[0]['hostGroupID']

        return group_id

    def create_connector(self, name):
        exists, id = self._does_connector_exist(name)
        if not exists:
            hg = self.dsm.host_group_create(name=name)
            ids = self.dshosts_that_map_to_kubenodes()
            self.dsm.host_move_to_hosts_group(ids, hg['ID'])
            return "Kubernetes connector %s created succesfully" % name
        else:
            return "Kubernetes connector with that name already exists"

    def end_session(self):
        self.dsm.end_session()

