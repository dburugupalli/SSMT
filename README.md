## Openshift Reporting Backend

OpenShift Reporting uses metering operator as backend.

More Details about Metering Operator [Metering Operator](https://docs.openshift.com/container-platform/4.3/metering/metering-installing-metering.html)

### Prerequisites 

1. OpenShift Account as Cluster Administrator

2. Locally running OpenShift Cluster [CRC](https://developers.redhat.com/products/codeready-containers). Refer this [CRC for Openshift Reporting Backend](https://github.com/dburugupalli/SSMT/blob/feature-1/Documentation/Installing_crc.md). 

3. Enable Alerting,monitoring, telemetry on CRC cluster using following commands

```bash
oc scale --replicas=1 statefulset --all -n openshift-monitoring; 
oc scale --replicas=1 deployment --all -n openshift-monitoring
```
Note: if the above commands donot work, Please refer [CRC for Openshift Reporting Backend](https://github.com/dburugupalli/SSMT/blob/feature-1/Documentation/Installing_crc.md) under 'Error in starting Monitoting, Telemetry and Alerting Section'


### Installation

#### Metering Operator Installation for local OCP cluster. 

``` bash
# Login as the Cluster Administrator
 
a. Create a namespace openshift-metering 
b. Label the namespace with `openshift.io/cluster-monitoring=true`
c. Search Red Hat Metering under Operator Hub and Click Install. 
d. Wait until Metering Operator pods are up and Running successfully.

# Output after these steps
NAME                                  READY   STATUS              RESTARTS   AGE

metering-operator-68dd64cfb6-pxh8v    2/2     Running             0          2m49s
```

#### Installing Metering Stack / Metering Configuration for local OCP cluser

Understanding [Metering Configuration](https://docs.openshift.com/container-platform/4.3/metering/configuring_metering/metering-about-configuring.html#metering-about-configuring)

At a minimum, you need to configure persistent storage and configure the Hive metastore.[Refer Samples](https://docs.openshift.com/container-platform/4.3/metering/configuring_metering/metering-about-configuring.html#metering-about-configuring)


```bash
$ oc project openshift-metering
$ oc create -f https://raw.githubusercontent.com/dburugupalli/SSMT/feature-1/openshift-metering-templates/configuration-templates/metering-configuration.yaml
 
# Wait until Componenets of metering stack are installed like hive metastore, presto database and 
# reporting operator 

$ oc -n openshift-metering get pods
NAME                                 READY   STATUS    RESTARTS   AGE
hive-metastore-0                     2/2     Running   14         7d15h
hive-server-0                        3/3     Running   21         7d15h
metering-operator-86b95669bb-njp4q   2/2     Running   14         7d15h
presto-coordinator-0                 2/2     Running   8          7d2h
reporting-operator-978687d9c-vkzrl   2/2     Running   27         7d15h
# to view custom resource definations
$ oc get crd | grep metering
hivetables.metering.openshift.io                            2020-05-19T04:34:42Z
meteringconfigs.metering.openshift.io                       2020-05-19T04:34:42Z
prestotables.metering.openshift.io                          2020-05-19T04:34:42Z
reportdatasources.metering.openshift.io                     2020-05-19T04:34:42Z
reportqueries.metering.openshift.io                         2020-05-19T04:34:42Z
reports.metering.openshift.io                               2020-05-19T04:34:42Z
storagelocations.metering.openshift.io                      2020-05-19T04:34:42Z
```

#### Verify Metering Stack / Configuration for local OCP cluster 

```bash
oc get reportdatasources -n openshift-metering | grep -v raw
```
Metering stack creates sample instances of reportdatasource and reportqueries custom resources. 

### Creating Reports 

For Now, lets use the pre-defined reportdatasources and reportqueries to generate our first report

```bash
$ oc project openshift-metering
$ oc create -f https://raw.githubusercontent.com/dburugupalli/SSMT/feature-1/openshift-metering-templates/reports-templates/namespace-cpu-request-hourly.yaml
$ meteringRoute="$(oc get routes metering -o jsonpath='{.spec.host}')"
$ echo "$meteringRoute"
$ token="$(oc whoami -t)"
$ reportName=namespace-cpu-request-hourly
$ reportFormat=json
# Change reportForma=csv to get output in csv format
$ curl --insecure -H "Authorization: Bearer ${token}" "https://${meteringRoute}/api/v1/reports/get?name=${reportName}&namespace=openshift-metering&format=$reportFormat"
```
To view reports on the terminal. 

### Defining Report-Query and ReportDataSources to acheive specific functionality

#### What if we want to define our own reportquery and reportdatasource custom resources, to achieve specific functionality ? 

Yes, We can define our own reportquery and reportdatasource

##### Define Reportdatasource custom resource, 

it contains PromQL queries. We can write our own promQL queries to create datasource and achieve our functionality 

```bash
...
spec:
  prometheusMetricsImporter:
    query: |
      sum(kube_pod_container_resource_requests_cpu_cores) by (pod, namespace, node)
.....
```

##### Define ReportQuery custom resource

if you inspect one reportquery custom resource, it contains SQL like queries. We can write our own SQL queries to achieve specific purpose. Presto Database provides functionality to execute SQL like queries. Presto has a dependency on Hive, and uses Hive for keeping metadata about the data Presto is working with.

```bash 
oc edit reportquery pod-cpu-request
```
```bash 
# output
# it takes various parameters as inputs, if we observe the yaml template
....
  query: |
    SELECT
      timestamp '{| default .Report.ReportingStart .Report.Inputs.ReportingStart| prestoTimestamp |}' AS period_start,
      timestamp '{| default .Report.ReportingEnd .Report.Inputs.ReportingEnd | prestoTimestamp |}' AS period_end,
      pod,
      namespace,
      node,
      sum(pod_request_cpu_core_seconds) as pod_request_cpu_core_seconds
    FROM {| dataSourceTableName .Report.Inputs.PodCpuRequestRawDataSourceName |}
    WHERE "timestamp" >= timestamp '{| default .Report.ReportingStart .Report.Inputs.ReportingStart | prestoTimestamp |}'
    AND "timestamp" < timestamp '{| default .Report.ReportingEnd .Report.Inputs.ReportingEnd | prestoTimestamp |}'
    AND dt >= '{| default .Report.ReportingStart .Report.Inputs.ReportingStart | prometheusMetricPartitionFormat |}'
    AND dt <= '{| default .Report.ReportingEnd .Report.Inputs.ReportingEnd | prometheusMetricPartitionFormat |}'
    GROUP BY namespace, pod, node
    ORDER BY namespace, pod, node ASC, pod_request_cpu_core_seconds DESC
...
```
Above queries gets the data in descending order. Lets, Define SQL query to get data in ascending order4

To get the data in ascending order, execute the following commands 

```bash 
oc delete reportquery pod-cpu-request
oc create -f https://raw.githubusercontent.com/dburugupalli/SSMT/feature-1/openshift-metering-templates/reportquery-templates/create-pod-cpu-request-reportquery.yaml
```
When the report is created, data will be populated in ascending order

##### Start the Flask web server using the following commands
```bash
# Create list-v1-projects-hourly report and reportquery 
oc create -f https://raw.githubusercontent.com/dburugupalli/SSMT/feature2/openshift-metering-templates/reportquery-templates/list-all-projects-v1-reportquery.yaml
oc create -f https://raw.githubusercontent.com/dburugupalli/SSMT/feature2/openshift-metering-templates/reports-templates/list-all-projects-v1-hourly.yaml
# Wait for some time untilhttps://raw.githubusercontent.com/dburugupalli/SSMT/feature2/openshift-metering-templates/reports-templates/list-all-projects-v1-hourly.yaml reports get generated.
# Install the python dependencies
pip install flask 
pip install flask_cors
pip install requests
# Set the Environment variables
. config.sh 
# Start the backend appplication server.
python3 app.py
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

