class Node:
    def __init__(self, name, status, roles, age, version, agent_status, am, wr, dpi, fw, im, li, tum):
        self.name = name
        self.status = status
        self.roles = roles
        self.age = age
        self.version = version
        self.agent_status = agent_status
        self.am =am
        self.dpi = dpi
        self.fw = fw
        self.im = im
        self.li = li
        self.wr = wr
        self.tum = tum

    def __repr__(self):
        return str(self.__dict__)

class KubeNode():

    addresses = []

    def __init__(self, name, addresses, os, container_runtime, kubelet_version, status, age, role):
        self.name = name
        self.addresses = addresses
        self.os = os
        self.container_runtime = container_runtime
        self.kubelet_version = kubelet_version
        self.status = status
        self.age = age
        self.role = role
