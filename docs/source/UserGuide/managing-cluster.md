# Managing Cluster

After a cluster is created, you can use CloudTik to manage the cluster and submit jobs.

### Status and Information

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

Here are examples to execute these CloudTik CLI commands on GCP clusters.

```
$ cloudtik status /path/to/your-cluster-config.yaml
 
Total 2 nodes. 2 nodes are ready
+---------------------+----------+-----------+-------------+---------------+---------------+-----------------+
|       node-id       | node-ip  | node-type | node-status | instance-type |   public-ip   | instance-status |
+---------------------+----------+-----------+-------------+---------------+---------------+-----------------+
| 491xxxxxxxxxxxxxxxxx| 10.0.x.x |    head   |  up-to-date | n2-standard-4 | 23.xxx.xx.xxx |     RUNNING     |
| 812xxxxxxxxxxxxxxxx | 10.0.x.x |   worker  |  up-to-date | n2-standard-4 |      None     |     RUNNING     |
+---------------------+----------+-----------+-------------+---------------+---------------+-----------------+
```

Show cluster summary information and useful links to connect to cluster web UI.

```
$ cloudtik info /path/to/your-cluster-config.yaml
 
Cluster small is: RUNNING
1 worker(s) are running

Runtimes: ganglia, spark

The total worker CPUs: 4.
The total worker memory: 16.0GB.

Key information:
    Cluster private key file: *.pem
    Please keep the cluster private key file safe.

Useful commands:
  Check cluster status with:
...

```

Show process status of cluster nodes.

```
$ cloudtik process-status /path/to/your-cluster-config.yaml
 
Total 2 live nodes reported.
+----------+-----------+--------------+-----------+-----------+--------------+-----------+----------+
| node-ip  | node-type | n-controller | n-manager | l-monitor | c-controller | r-manager | r-server |
+----------+-----------+--------------+-----------+-----------+--------------+-----------+----------+
| 10.0.x.x |    head   |   running    |     -     |  sleeping |   sleeping   |  sleeping | sleeping |
| 10.0.x.x |   worker  |   running    |  sleeping |  sleeping |      -       |     -     |    -     |
+----------+-----------+--------------+-----------+-----------+--------------+-----------+----------+
```

Show debug status of cluster scaling.

```
$ cloudtik debug-status /path/to/your-cluster-config.yaml

======== Cluster Scaler status: 2022-05-12 08:46:49.897707 ========
Node status
-------------------------------------------------------------------
Healthy:
 1 head-default
 1 worker-default
Pending:
 (no pending nodes)
Recent failures:
 (no failures)
```

Check cluster is whether healthy.

```
$ cloudtik health-check  /path/to/your-cluster-config.yaml
Cluster is healthy.
```

### Attach to Cluster Nodes

Connect to a terminal of cluster head node.

```
cloudtik attach /path/to/your-cluster-config.yaml -y
```

Then you will log in head node of the cluster vis SSH as below

```
$ cloudtik attach /home/wh/cloud/gcp/small.yaml
(base) ubuntu@cloudtik-example-head-a7xxxxxx-compute:~$

```

Log in to worker node with `--node-ip` as below

```
$ cloudtik attach --node-ip 10.0.1.5 /home/wh/cloud/gcp/small.yaml
(base) ubuntu@cloudtik-example-worker-150xxxxx-compute:~$
```

### Execute and Submit Jobs

Execute a command via SSH on a cluster or a specified node.

```
cloudtik exec /path/to/your-cluster-config.yaml
```

For example, list the items under $USER directory as below.  

```
$ cloudtik exec /path/to/your-cluster-config.yaml ls
anaconda3  cloudtik_bootstrap_config.yaml  cloudtik_bootstrap_key.pem  jupyter  runtime
```

Submit job to cluster to run.

```
cloudtik submit /path/to/your-cluster-config.yaml [job-file (py|sh|scala)]
```

#### Run TPC-DS on Spark cluster

Here is the example of running TPC-DS on Spark cluster with `cloudtik submit`  

##### 1. Creating a cluster

To generate data and run TPC-DS on Cloudtik cluster, some tools must be installed in advance.
We provide a script to simplify the installation of these dependencies. You only need to add the following bootstrap_commands to the cluster configuration file.

```buildoutcfg

bootstrap_commands:
    - wget -P ~/ https://raw.githubusercontent.com/oap-project/cloudtik/main/tools/spark/benchmark/scripts/bootstrap-benchmark.sh &&
        bash ~/bootstrap-benchmark.sh  --tpcds
```

##### 2. Generating data

We provided the datagen scala script which can be found from CloudTik's `./tools/spark/benchmark/scripts/tpcds-datagen.scala` for you to generate data in different size.

Execute the following command to submit and run the datagen script on the cluster,

```
cloudtik submit /path/to/your-cluster-config.yaml ./tools/spark/benchmark/scripts/tpcds-datagen.scala --conf spark.driver.scaleFactor=1 --conf spark.driver.fsdir="s3a://s3_bucket_name" --jars \$HOME/runtime/benchmark-tools/spark-sql-perf/target/scala-2.12/spark-sql-perf_2.12-0.5.1-SNAPSHOT.jar
```
Replace the cluster configuration file, the paths, spark.driver.scale, spark.driver.fsdir values in the above command for your case.

##### 3. Run TPC-DS power test

We provided the power test scala script which can be found from CloudTik's `./tools/spark/benchmark/scripts/tpcds-power-test.scala` for users to run TPC-DS power test with Cloudtik cluster.

Execute the following command to submit and run the power test script on the cluster,

```buildoutcfg
cloudtik submit your-cluster-config.yaml $CLOUTIK_HOME/tools/spark/benchmark/scripts/tpcds-power-test.scala --conf spark.driver.scaleFactor=1 --conf spark.driver.fsdir="s3a://s3_bucket_name" --conf spark.sql.shuffle.partitions=\$(cloudtik head info --worker-cpus) --conf spark.driver.iterations=1 --jars \$HOME/runtime/benchmark-tools/spark-sql-perf/target/scala-2.12/spark-sql-perf_2.12-0.5.1-SNAPSHOT.jar
```

Replace the cluster configuration file, the paths, spark.driver.scale, spark.driver.fsdir, spark.driver.iterations values in the above command for your case. 


### Manage Files

Upload files or directories to cluster:

``` 
cloudtik rsync-up /path/to/your-cluster-config.yaml [source] [target]
```
  
Download files or directories from cluster

```
cloudtik rsync-down /path/to/your-cluster-config.yaml [source] [target]
```

### Start or Stop Runtime Services

```
cloudtik runtime start /path/to/your-cluster-config.yaml
cloudtik runtime stop /path/to/your-cluster-config.yaml
```

### Scale Up or Scale Down Cluster

Scale up the cluster with a specific number cpus or nodes.

Try with `--cpus`

```
$ cloudtik scale  --cpus 12 /path/to/your-cluster-config.yaml
Are you sure that you want to scale cluster small to 12 CPUs? Confirm [y/N]: y

Shared connection to 23.xxx.xx.xxx closed.

$ cloudtik info /path/to/your-cluster-config.yaml
Cluster small is: RUNNING
2 worker(s) are running

Runtimes: ganglia, spark

The total worker CPUs: 8.
The total worker memory: 32.0GB.
...

```

Try to specify with `--nodes`.

```
$ cloudtik scale --nodes 4  /path/to/your-cluster-config.yaml
Are you sure that you want to scale cluster small to 4 nodes? Confirm [y/N]: y

Shared connection to 23.xxx.xx.xxx closed.
$ cloudtik info /path/to/your-cluster-config.yaml
Cluster small is: RUNNING
3 worker(s) are running

Runtimes: ganglia, spark

The total worker CPUs: 12.
The total worker memory: 48.0GB.

Key information:
...

```

### Access the Web UI

```
The SOCKS5 proxy to access the cluster Web UI from local browsers:
    localhost:6001

Ganglia Web UI:
    http://<head-internal-ip>/ganglia
YARN ResourceManager Web UI:
    http://<head-internal-ip>:8088
Spark History Server Web UI:
    http://<head-internal-ip>10.0.0.4:18080
Jupyter Web UI:
    http://<head-internal-ip>:8888, default password is 'cloudtik'
```


For more information as to the commands, you can use `cloudtik --help` or `cloudtik [command] --help` to get detailed instructions.