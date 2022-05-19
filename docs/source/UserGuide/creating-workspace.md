# Creating Workspace

CloudTik uses **Workspace** concept to easily manage shared Cloud resources such as VPC, network, identity resources, 
firewall or security groups. Within one workspace, you can start one or multiple clusters.

CloudTik will help users quickly create and configure:

- VPC shared by all the clusters of the workspace. 

- A private subnet for workers and a public subnet for head node. 

- Firewall rules for SSH access to head node and internal communication. 

- A NAT gateway for Internet access. 

- An identity for head node to Cloud API.


## Create a Workspace Configuration File

### AWS

Here is an AWS workspace configuration yaml example, which can find at CloudTik's `example/cluster/aws/example-workspace.yaml` 

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
          # restrict IpRanges here according to your cluster for security
          IpRanges:
          - CidrIp: 0.0.0.0/0
```

*NOTE:* Remember to change `CidrIp` from `0.0.0.0/0` to restricted IpRanges for TCP port 22 security


### Azure

Here is an Azure workspace configuration yaml example, which can find at CloudTik's `example/cluster/azure/example-workspace.yaml`

```
# A unique identifier for the workspace.
workspace_name: example-workspace

# Cloud-provider specific configuration.
provider:
    type: azure
    location: westus
    subscription_id: your_subscription_id
    # Use securityRules to allow SSH access from your working node
    securityRules:
      - priority: 1000
        protocol: Tcp
        access: Allow
        direction: Inbound
        source_address_prefixes:
          - 0.0.0.0/0
        source_port_range: "*"
        destination_address_prefix: "*"
        destination_port_range: 22

```

*NOTE:* Remember


### GCP

```
# A unique identifier for the workspace.
workspace_name: example-workspace

# Cloud-provider specific configuration.
provider:
    type: gcp
    region: us-central1
    availability_zone: us-central1-a
    project_id: your_project_id
    firewalls:
        # Use firewall_rules to allow SSH access from your working node
        firewall_rules:
          - allowed:
              - IPProtocol: tcp
                ports:
                  - 22
            sourceRanges:
              - 0.0.0.0/0

```

*NOTE:* Remember

### Create or Delete a Workspace

Use the following command to create and provision a workspace:

```
cloudtik workspace create /path/to/<your-workspace-config>.yaml
```

A typical workspace configuration file is usually very simple. Specify the unique workspace name, cloud provider type
and a few provider-specific properties. 


Use the following command to delete a workspace:

```
cloudtik workspace delete /path/to/<your-workspace-config>.yaml
```

Check `./example/cluster` folder for more Workspace configuration file examples.
