# Building CloudTik

## Building CloudTik from Source

### Python Environment

CloudTik requires a Python environment to run. We suggest you use Conda to manage Python environments and packages. If you don't have Conda , you can refer ```dev/install-conda.sh``` to install conda on Ubuntu systems.

```
cd cloudtik && bash dev/install-conda.sh
```

Once Conda is installed, create an environment specify a Python version as below. 
CloudTik currently supports Python 3.6, 3.7, 3.8, 3.9. Here we take Python 3.7 as example.

```
conda create -n cloudtik -y python=3.7;
conda activate cloudtik;
```

### Building CloudTik wheels with our provided script

After create a Python environment as above, then build cloudtik wheel for Linux.

Run the following command to start the build.

```
bash build.sh
```
Then under `./python/dist` directory, you will find the `*.whl` which is your current Python version's CloudTik wheel for Linux.

### Installing CloudTik

If you want to install the CloudTik built above into the clusters to create, and you have it uploaded to cloud or servers where can be visited. 

Add `cloudtik_wheel_url` to your cluster config yaml file as below.

```
workspace_name: ...

cluster_name: ...

cloudtik_wheel_url: "/link/to/cloudtik-*.whl"

```
