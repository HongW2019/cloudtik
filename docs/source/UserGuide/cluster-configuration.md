#  Cluster Configuration

Before launching a cluster on cloud providers with CloudTik, we need follow several steps below.

This section provides instructions for configuring CloudTik on various cloud providers or a local cluster.

## Configure Cluster yaml file

### Step 0. Setting Credentials for Cloud Providers

After `pip` install CloudTik, then configure or log into your Cloud account to gain access to corresponding cloud provider API.

#### AWS

Please follow the instructions described in [the AWS docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) to configure AWS credentials.

#### Azure

Use `az login` to log into your Azure cloud account.

#### GCP

Create a service account then set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable as described in [the GCP docs](https://cloud.google.com/docs/authentication/getting-started).

### Step 1. Create a workspace for your clusters.

CloudTik uses **Workspace** concept to manage your Cloud network and other resources. Within one workspace, you can start one or multiple clusters.

Use the following command to create and provision a workspace:

```
cloudtik workspace create /path/to/<your-workspace-config>.yaml
```

A typical workspace configuration file is usually very simple. Specific the unique workspace name, cloud provider type
and a few cloud provider specific properties. 

Here take AWS for example.

```
# A unique identifier for the workspace.
workspace_name: example-workspace

# Cloud-provider specific configuration.
provider:
    type: aws
    region: us-west-2
    security_group:
        # Use IpPermissions to allow SSH access from your working node
        IpPermissions:
        - FromPort: 22
          ToPort: 22
          IpProtocol: TCP
          IpRanges:
          - CidrIp: 0.0.0.0/0
```

Check `./example/cluster` folder for more Workspace configuration file examples.


### Step 2. Configure Cloud Storage 

If you choose cloud storage for your clusters, additionally, configure cloud storage for corresponding cloud provider as below.

#### AWS

#### Azure

#### GCP

If you do not already have a GCS bucket, create one and configure its permission for your service account.
More details, please refer to [gcs bucket guide](../QuickStart/configure-gcs-bucket.md).

### Step 3. Fill out required field in cluster yaml

A typical cluster configuration file is usually very simple thanks to CloudTik hierarchy templates design. 

AWS docker-based cluster configuration file is shown below.

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

#### GCP 

GCP host-based cluster configuration example is shown below.

```
# An example of standard 1 + 3 nodes cluster with standard instance type
from: gcp/standard

# A unique identifier for the cluster.
cluster_name: example-standard

# Workspace into which to launch the cluster
workspace_name: exmaple-workspace

# Cloud-provider specific configuration.
provider:
    type: gcp
    region: us-central1
    availability_zone: us-central1-a
    project_id: your_project_id
    # GCS configurations for storage
    gcp_cloud_storage:
        gcs.bucket: your_gcs_bucket
        gcs.service.account.client.email: your_service_account_client_email
        gcs.service.account.private.key.id: your_service_account_private_key_id
        gcs.service.account.private.key: your_service_account_private_key

# How CloudTik will authenticate with newly launched nodes.
auth:
    ssh_user: ubuntu
    # Set proxy if you are in corporation network. For example,
    # ssh_proxy_command: "ncat --proxy-type socks5 --proxy your_proxy_host:your_proxy_port %h %p"

available_node_types:
    worker-default:
        # The minimum number of worker nodes to launch.
        min_workers: 3

```

After create a service account on GCP in step 0, you can the JSON file and get service account key of it, then fill them out to cluster configuration file `gcp_cloud_storage` above.

Refer to `example/cluster` folder for more cluster configurations examples of different cloud providers.

Now you can start to create a cluster with CloudTik:

```
cloudtik start /path/to/<your-cluster-config>.yaml -y
```
