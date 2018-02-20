
Deep Security Kubernetes (kubectl) Plugin
====

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
#will move ds computers with names matching k8s node names into group<br/>
kubectl plugin ds connector_create "myk8sconnector"<br/><br/>
kubectl plugin ds connector_sync<br/>



#sample output
![Alt text](ds_kubectl_plugin.jpg)
