import sys
import base64
import json
import pytz
from datetime import datetime
from dsp3.models.manager import Manager
from kubernetes import client, config

def get_kubernetes_api_object():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    return v1

def get_host_details(dsm, host_id):
    status = {}
    host = dsm.host_status(host_id)

    status['Agent Status'] = host['overallStatus']
    status['AM'] = "Off" if "Off" in host['overallAntiMalwareStatus'] else "On"
    status['WR'] = "Off" if "Off" in host['overallWebReputationStatus'] else "On"
    status['DPI'] = "Off" if "Off" in host['overallDpiStatus'] else "On"
    status['FW'] = "Off" if "Off" in host['overallFirewallStatus'] else "On"
    status['IM'] = "Off" if "Off" in host['overallIntegrityMonitoringStatus'] else "On"
    status['LI'] = "Off" if "Off" in host['overallLogInspectionStatus'] else "On"
    trusted_update_mode = json.loads(dsm.get_trusted_update_mode(host_id))
    status['TUM'] = "Off" if "off" in trusted_update_mode['DescribeTrustedUpdateModeResponse']['state'] else "On"
    return status


def calculate_age(born):
    age = (datetime.now().replace(tzinfo=pytz.utc) - born).days
    return 1 if age == 0 else age

def get_node_role(labels):
    role = "<none>"
    for label in labels:
        if 'node-role.kubernetes.io' in label:
            role = label.split("/")[1]
    return role

def get_ds_password(kube_api):
    secrets = kube_api.list_secret_for_all_namespaces().items
    password = None
    for secret in secrets:
        if secret.metadata.name == 'deepsecurity':
            password = base64.b64decode(secret.data['password']).decode('utf-8')

    return password


def get_ds_api_object(config, kube_api):
    dsm = None
    using_dsas = config['using_dsas']
    username = config['ds_username']
    password = get_ds_password(kube_api)
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