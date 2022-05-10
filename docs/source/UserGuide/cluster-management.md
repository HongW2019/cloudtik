# Managing Clusters

This section will introduce CloudTik usages about managing the created clusters in details.

#### Show cluster status and information

Use the following commands to show various cluster information.
```
cloudtik status /path/to/your-cluster-config.yaml
cloudtik info /path/to/your-cluster-config.yaml
cloudtik head-ip /path/to/your-cluster-config.yaml
cloudtik worker-ips /path/to/your-cluster-config.yaml
cloudtik process-status /path/to/your-cluster-config.yaml
cloudtik monitor /path/to/your-cluster-config.yaml
```
#### Attach to the cluster head (or specific node)
```
cloudtik attach your-cluster-config.yaml
```
#### Execute commands on cluster head (or specified node or on all nodes)
```
cloudtik exec your-cluster-config.yaml
```
#### Submit a job to the cluster to run
```
cloudtik submit your-cluster-config.yaml your-job-file.(py|sh|scala)
```
#### Copy local files to cluster head (or to all nodes)
```
cloudtik rsync-up your-cluster-config.yaml [source] [target]
```
#### Copy file from cluster to local
```
cloudtik rsync-down your-cluster-config.yaml [source] [target]
```
#### Stop a cluster
```
cloudtik stop your-cluster-config.yaml
```
For more information as to the commands, you can use `cloudtik --help` or `cloudtik [command] --help` to get detailed instructions.
