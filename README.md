# CloudTik

CloudTik is a cloud scaling platform for scaling your distributed analytics and AI cluster such as Spark easily
on public Cloud environment including AWS, Azure, GCP and so on. The CloudTik target is enable any users can
easily create and manage analytics and AI clusters, provide out of box optimized Spark runtime for
your Analytics and AI needs, and go quickly to focus on your workload and business need instead
of taking a lot of time constructing the cluster and platform. We target:
- Support major public Cloud providers (AWS, Azure and GCP, ...)
- Out of box and optimized Spark runtime for Analytics and AI
- Easy and unified operation experiences across Cloud
- Open architecture and user full control
- Runtime directly on VM or in Container
- A full open-sourced solution

## Getting Started with CloudTik

### 1. Preparing Python environment

CloudTik requires a Python environment on Linux, we recommend using Conda to manage Python environments and packages.

If you don't have Conda installed, please refer to `dev/install-conda.sh` to install Conda on Linux.

```
git clone https://github.com/oap-project/cloudtik.git && cd cloudtik
bash dev/install-conda.sh
```

Once Conda is installed, create an environment with a specific Python version as below.
CloudTik currently supports Python 3.7, 3.8, 3.9. Here we take Python 3.7 as an example.

```
conda create -n cloudtik -y python=3.7
conda activate cloudtik
```

### 2. Installing CloudTik

Execute the following `pip` commands to install CloudTik on your working machine for specific cloud providers. 

Here we take AWS as an example.

```
# if running CloudTik on aws
pip install -U "cloudtik[aws] @ https://d30257nes7d4fq.cloudfront.net/downloads/cloudtik/cloudtik-0.9.0-cp37-cp37m-manylinux2014_x86_64.whl"
```

Replace `cloudtik[aws]` with `clouditk[azure]` or `cloudtik[gcp]` if you want to create clusters on Azure or GCP.
Use `cloudtik[all]` if you want to manage clusters with all supported Cloud providers.

You can install the latest CloudTik wheels via the following links. These daily releases do not go through the full release process.

| Linux      | Installation                                                                                                                                       |
|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------------|
| Python 3.9 | `pip install -U "cloudtik[aws] @ https://d30257nes7d4fq.cloudfront.net/downloads/cloudtik/cloudtik-0.9.0-cp39-cp39-manylinux2014_x86_64.whl" `     |
| Python 3.8 | `pip install -U "cloudtik[aws] @ https://d30257nes7d4fq.cloudfront.net/downloads/cloudtik/cloudtik-0.9.0-cp38-cp38-manylinux2014_x86_64.whl" `     |
| Python 3.7 | `pip install -U "cloudtik[aws] @ https://d30257nes7d4fq.cloudfront.net/downloads/cloudtik/cloudtik-0.9.0-cp37-cp37m-manylinux2014_x86_64.whl" `    |


### 3. Authentication to Cloud Providers API

After CloudTik is installed on your working machine, then you need to configure or log into your Cloud account to 
gain access to cloud provider API on this machine.

#### AWS

First, install AWS CLI(command line interface), please refer to
[AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) 
for detailed instructions.

After AWS CLI is installed, then you need configure AWS CLI about credentials, the quickest way to configure 
is to run `aws configure` command, you can refer to
[managing access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey) 
to get *AWS Access Key ID* and *AWS Secret Access Key*.

More ways to configure AWS CLI can be found from the [guide](https://github.com/aws/aws-cli/tree/v2#getting-started).

#### Azure

After CloudTik is installed on your working machine, login to Azure using `az login` and set the subscription to use 
from the command line (`az account set -s <subscription_id>`). You can follow the
[Azure guide](https://docs.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id#find-your-azure-subscription)
to find your Azure subscription id.

Then the Azure CLI is configured to manage resources on your Azure account.

#### GCP

First, follow the [Google Cloud docs](https://cloud.google.com/docs/authentication/getting-started#creating_a_service_account) 
to create a service account on Google Cloud, A JSON file should be safely downloaded and kept by you after the
service account created.

Then set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable as described in
[GCP docs](https://cloud.google.com/docs/authentication/getting-started#setting_the_environment_variable) on your working machine.

### 4. Creating a Workspace for Clusters.

CloudTik uses **Workspace** concept to easily manage shared Cloud resources such as VPC, network, identity resources, 
firewall or security groups. In a Workspace, you can start one or more clusters.

Create a configuration workspace yaml file to specify the unique workspace name, cloud provider type and a few cloud 
provider properties. 

Take AWS as an example.

```
# A unique identifier for the workspace.
workspace_name: example-workspace

# Cloud-provider specific configuration.
provider:
    type: aws
    region: us-west-2
    security_group:
        # Use IpPermissions to allow SSH access from your working node
        # Remember to restrict IpRanges for security 
        IpPermissions:
        - FromPort: 22
          ToPort: 22
          IpProtocol: TCP
          IpRanges:
          - CidrIp: 0.0.0.0/0
```
*NOTE:* Remember to change `CidrIp` from `0.0.0.0/0` to restricted IpRanges for TCP port 22 security.

Use the following command to create and provision a Workspace:

```
cloudtik workspace create /path/to/your-workspace-config.yaml
```

Check `example/cluster` folder for more Workspace configuration file examples.

### 5. Configuring Cloud Storage

If you choose cloud storage as file system or to store stage and event data, cloud storage account is needed.

After follow the guides below for specific cloud provider, you will be able to fill out the corresponding storage filed 
of your cluster configuration yaml. 

#### AWS

Every object in Amazon S3 is stored in a bucket. Before you can store data in Amazon S3, you must create a bucket.

Please refer to the S3 [guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html) for instructions.
The name of S3 bucket will be used in next step.

#### Azure

Create an Azure storage account, and a storage container within this storage account.

Azure **Blob storage** or **Data Lake Storage Gen2** are both supported by CloudTik. Please refer to Azure related 
[guides](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal) for details.

The name of storage account and storage container will be used when configuring Azure cluster yaml.

#### GCP

If you do not already have a GCS bucket, create one by following the 
[guide](https://cloud.google.com/storage/docs/creating-buckets#create_a_new_bucket).

Then set its permission for this bucket, please refer to [gcs bucket guide](gcs-bucket.md) for more details.
The name of bucket will be used when configuring GCP cluster yaml.

### 6. Starting a cluster

Now you can start a cluster:

```
cloudtik start /path/to/your-cluster-config.yaml
```

A typical cluster configuration file is usually very simple thanks to CloudTik hierarchy templates design.

Take AWS as an example, this example can be found from CloudTik's `example/cluster/aws/example-standard.yaml`.

```
# An example of standard 1 + 3 nodes cluster with standard instance type
from: aws/standard

# Workspace into which to launch the cluster
workspace_name: example-workspace

# A unique identifier for the cluster.
cluster_name: example-docker

# Enable container
docker:
    enabled: True

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

You need the cloud storage access information in Step 5 and only a few additional key settings in the configuration file to launch a cluster.

As for `aws_s3_storage` above: 

> `s3.bucket`: name of S3 bucket that you created.
> 
> `s3.access.key.id`:  your AWS Access Key ID.
> 
> `s3.secret.access.key`:  your AWS Secret Access Key.

 *AWS Access Key ID* and *AWS Secret Access Key* can be found from the AWS guide of
[managing access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).

As for `auth` above, if your working node is using corporation network, please set proxy as below.

```
auth:
    ssh_user: ubuntu
    ssh_proxy_command: "ncat --proxy-type socks5 --proxy <your_proxy_host>:<your_proxy_port> %h %p"
```

Refer to `example/cluster` for more cluster configurations examples.

### 7. Managing clusters

CloudTik provides very powerful capability to monitor and manage the cluster.

#### Cluster status and information

Use the following commands to show various cluster information.

```
# Check cluster status with:
cloudtik status /path/to/your-cluster-config.yaml
# Show cluster summary information and useful links to connect to cluster web UI.
cloudtik info /path/to/your-cluster-config.yaml
cloudtik head-ip /path/to/your-cluster-config.yaml
cloudtik worker-ips /path/to/your-cluster-config.yaml
cloudtik process-status /path/to/your-cluster-config.yaml
cloudtik monitor /path/to/your-cluster-config.yaml
cloudtik debug-status /path/to/your-cluster-config.yaml
cloudtik health-check  /path/to/your-cluster-config.yaml
```
#### Attach to the cluster head (or specific node)

Connect to a terminal of cluster head node.

```
cloudtik attach /path/to/your-cluster-config.yaml
```

Log in to worker node with `--node-ip` as below.

```
cloudtik attach --node-ip x.x.x.x /path/to/your-cluster-config.yaml
```

#### Execute and Submit Jobs

Execute a command via SSH on cluster head node or a specified node.

```
cloudtik exec /path/to/your-cluster-config.yaml [command]
```

Execute commands on specified worker node 

```
cloudtik exec your-cluster-config.yaml --node-ip=x.x.x.x [command]
```


#### Manage Files

Upload files or directories to cluster:

``` 
cloudtik rsync-up /path/to/your-cluster-config.yaml [source] [target]
```
  
Download files or directories from cluster

```
cloudtik rsync-down /path/to/your-cluster-config.yaml [source] [target]
```

#### Start or Stop Runtime Services

```
cloudtik runtime start /path/to/your-cluster-config.yaml
cloudtik runtime stop /path/to/your-cluster-config.yaml
```

#### Scale Up or Scale Down Cluster

Scale up the cluster with a specific number cpus or nodes.

Try with `--cpus` or `--nodes`.

```
cloudtik scale --cpus xx /path/to/your-cluster-config.yaml
cloudtik scale --nodes x /path/to/your-cluster-config.yaml
```

For more information as to the commands, you can use `cloudtik --help` or `cloudtik [command] --help` to get detailed instructions.
