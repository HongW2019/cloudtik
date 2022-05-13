# Creating Cluster

The cluster configuration is defined within a YAML file that will be used by CloudTik to launch nodes and its cluster
controller on head node to launch worker nodes.

CloudTik offers cluster configuration yaml examples, which are located under CloudTik's `example/cluster/` directory.
 
Please follow instructions below to customize your cluster configuration.

## Controlling the Number of Workers

The minimum number of worker nodes to launch. Default number is 1, you can change it according to your use case by 

adding configuration to the cluster configuration yaml file to overwrite default as below, which sets minimum number of worker nodes to 3.

```
available_node_types:
    worker.default:
        min_workers: 3
```

## Choosing Runtimes for Cluster

CloudTik introduces **Runtime** concept to integrate different analytics and AI framework to deploy into clusters.

- **Spark**,  a multi-language engine for executing data engineering, data science, and machine learning.

- **HDFS**, a distributed file system designed to run on commodity hardware.

- **Ganglia**, a scalable distributed monitoring system for high-performance computing systems such as clusters and Grids.

- **Metastore**, a service that stores metadata related to Apache Hive and other services.

- **Presto**, a distributed SQL query engine for running interactive analytic queries against data sources of all sizes.

- **ZooKeeper**, a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services.

- **Kafka**, a community distributed event streaming platform capable of handling trillions of events a day.

Default runtimes contains ganglia and Spark, you can add more runtimes according to demands of your cluster.

For example, if you want use HDFS as file system instead of cloud storage, please add configuration to your cluster yaml file as below.

```
runtime:
    types: [ganglia, hdfs, spark]
```

## Customizing Setup Steps

CloudTik will install and config Conda, Python, selected Runtimes and other requirements to your head and workers on setup step.

If you want to add more integrations to your clusters within the setup steps, such as adding required tools to run TPC-DS, 
please add the following `bootstrap_commands` section to your cluster yaml file, which will install TPC-DS and required packages
with specified scripts to set up nodes after all common setup commands finish.

```buildoutcfg

bootstrap_commands:
    - wget -P ~/ https://raw.githubusercontent.com/oap-project/cloudtik/main/tools/spark/benchmark/scripts/bootstrap-benchmark.sh &&
        bash ~/bootstrap-benchmark.sh  --tpcds
```


## Using Templates to Simplify Node Configuration

CloudTik designs the structure of inheritance to offer a series of cluster configuration templates.
Please refer to CloudTik's `python/cloudtik/templates` directory for configuration templates for different cloud providers.

Here is AWS standard template, which is located in CloudTik's `./python/cloudtik/templates/aws/standard.yaml`

```
# Cloud-provider specific configuration.
provider:
    type: aws

# The instance configuration for a standard instance type
available_node_types:
    head.default:
        node_config:
            InstanceType: m5.2xlarge
            BlockDeviceMappings:
                - DeviceName: /dev/sda1
                  Ebs:
                      VolumeSize: 100
                      VolumeType: gp2
                      DeleteOnTermination: True
    worker.default:
        node_config:
            InstanceType: m5.2xlarge
            BlockDeviceMappings:
                - DeviceName: /dev/sda1
                  Ebs:
                      VolumeSize: 100
                      VolumeType: gp2
                      DeleteOnTermination: True
                - DeviceName: /dev/sdf
                  Ebs:
                      VolumeSize: 200
                      VolumeType: gp3
                      # gp3: 3,000-16,000 IOPS
                      Iops: 5000
                      DeleteOnTermination: True


```

You can find `available_node_types` section providing with instances type examples for different cluster from small to very large cluster.

Then we also offer cluster configuration yaml example, which is located in CloudTik's `example/cluster/` directory.

Here also take [AWS standard cluster](../../../example/cluster/aws/example-standard.yaml) for example, it inherits
AWS standard template, which is set by `from: AWS/standard` as below.

```
# An example of standard 1 + 3 nodes cluster with standard instance type
# Inherits AWS standard template
from: aws/standard

# A unique identifier for the cluster.
cluster_name: example-standard

# Workspace into which to launch the cluster
workspace_name: exmaple-workspace

# Cloud-provider specific configuration.
provider:
    type: aws
    region: us-west-2
    # S3 configurations for storage
    aws_s3_storage:
        s3.bucket: your_s3_bucket
        s3.access.key.id: your_s3_access_key_id
        s3.secret.access.key: your_s3_secret_access_key

auth:
    ssh_user: ubuntu
    # Set proxy if you are in corporation network. For example,
    # ssh_proxy_command: "ncat --proxy-type socks5 --proxy your_proxy_host:your_proxy_port %h %p"

available_node_types:
    worker.default:
        # The minimum number of worker nodes to launch.
        min_workers: 3

```

Once the cluster configuration is defined and CloudTik is installed, you can use the following commands to create a cluster with CloudTik

```
$ cloudtik start /path/to/your-cluster-config.yaml -y
```

After that, you can use the CloudTik to monitor and manage your cluster.

Please refer to next guide: [managing clusters](./managing-cluster.md) for detailed instructions.
