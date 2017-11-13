
Deep Security Kubernetes (kubectl) Plugin
====

## Installation
clone repo to your ~/.kube/plugins directory

pip install -r requirements.txt


## Usage
kubectl plugin ds


#sample output
NAME        STATUS    ROLE    AGE    VERSION    Operating System    Container Runtime    DS AGENT STATUS    AM    WR    DPI    FW    IM    LI    TUM
----------  --------  ------  -----  ---------  ------------------  -------------------  -----------------  ----  ----  -----  ----  ----  ----  -----
k8smaster   Ready     master  1d     v1.8.3     Ubuntu 16.04.3 LTS  docker://1.12.6      Software Update:   On    On    Off    Off   Off   On    Off
k8sworker   Ready     <none>  1d     v1.8.3     Ubuntu 16.04.3 LTS  docker://1.12.6      Managed (Online)   Off   On    Off    Off   Off   On    Off
k8sworker2  Ready     <none>  1d     v1.8.3     Ubuntu 16.04.3 LTS  docker://1.12.6      Not Installed      NA    NA    NA     NA    NA    NA    NA
