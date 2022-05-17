# Creating Workspace

CloudTik uses **Workspace** concept to easily manage shared Cloud resources such as VPC, network, identity resources, 
firewall or security groups. Within one workspace, you can start one or multiple clusters.

![](../../image/high-level-architecture.png)

CloudTik will help users quickly create and configure:

- VPC shared by all the clusters of the workspace. 

- A private subnet for workers and a public subnet for head node. 

- Firewall rules for SSH access to head node and internal communication. 

- A NAT gateway for Internet access. 

- An identity for head node to Cloud API.


Use the following command to create and provision a workspace:

```
cloudtik workspace create /path/to/<your-workspace-config>.yaml
```

A typical workspace configuration file is usually very simple. Specify the unique workspace name, cloud provider type
and a few provider-specific properties. 

Here take AWS as an example. 
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

You need restrict IpRanges `CidrIp` above for TCP port 22 for VPC network firewall rules.

Use the following command to delete a workspace:

```
cloudtik workspace delete /path/to/<your-workspace-config>.yaml
```

Check `./example/cluster` folder for more Workspace configuration file examples.
