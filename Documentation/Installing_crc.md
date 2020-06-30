# CRC Installation for SSMT Backend

Code Ready Container can be used for Local Development using OpenShift.


## Prerequisites 

Please install these linux packages before installing Code Ready Container 

```bash
NetworkManager
libvirt
```

## Installation

Use the [CRC](https://access.redhat.com/documentation/en-us/red_hat_codeready_containers/1.7/html/getting_started_guide/installation_gsg) Documentation to download. 

Login using your redhat account and select OpenShift for Laptop & copy image pull Secret, this will be used later while installing CRC. 


Lets configure CRC cluster with 7+vcpus &16+GB

```bash
crc config set cpus 7
crc config set memory <memory-in-mb>
# To view crc configuration 
crc config view
crc setup
crc start
# Deleting the code ready container 
crc delete
```

Note:
To enable configuration changes, you must delete the existing CRC virtual machine and create a new one.

[CRC Version 1.6](https://github.com/code-ready/crc/releases/tag/1.6.0) download link 

## Some Common issues

#### Unable to login to crc cluster via web console. 

Use the following steps

```bash
crc ip # This will give the Virtual Machine IP address
# Make a note of the IP. Add the following lines using /etc/hosts files
# Ensure to replace vm_ip with your respective Virtual machine ip address
<vm_ip>   api.crc.testing
<vm_ip> oauth-openshift.apps-crc.testing
<vm_ip> console-openshift-console.apps-crc.testing

```
#### Error in starting Monitoring, Telemetry and Alerting
```bash
oc get clusterversion version -ojsonpath='{range .spec.overrides[*]}{.name}{"\n"}{end}' | nl -v 0
#  Replace the unmanged-operator-index to [0 cluster-monitoring-operator]
oc patch clusterversion/version --type='json' -p '[{"op":"remove", "path":"/spec/overrides/<unmanaged-operator-index>"}]' -oyaml

```

