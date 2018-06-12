
Deep Security Kubernetes (kubectl) Plugin
====

Note: This is an example plugin that demonstrates how easy it is to integrate cluster security policy visibility into kubectl
      with the Deep Security APIs.


## Installation
1. clone repo to your ~/.kube/plugins directory
2. pip install -r requirements.txt
3. Create a Kubernetes secret called deepsecurity with your base64 encoded password.
   A sample secret.yaml file is included. kubectl apply -f secret.yaml
4. Enter your DS information in config.yaml

* NOTE: DS computer name or IP must correspond to k8s node name


## Usage
Commands:<br/><br/>
kubectl plugin ds status<br/><br/>
#will assign policy to all nodes or single node if node name specified<br/>
kubectl plugin ds assign_policy policyname<br/>
kubectl plugin ds assign_policy policyname nodename<br/>



#sample output
![Alt text](ds_kubectl_plugin.jpg)
