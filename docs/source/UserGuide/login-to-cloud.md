# Login to Cloud

- [AWS](#AWS)
- [Azure](#Azure)
- [GCP](#GCP)

## AWS

### Login to AWS

Login to [AWS](https://console.aws.amazon.com/)

### Credentials

First, install boto (`pip install boto3`) and configure your AWS credentials in `~/.aws/credentials` as described in 
the [boto docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) on your working machine.

Once boto is configured to manage resources on your AWS account, you should be ready to launch your cluster.

### Creating a bucket

Every object in Amazon S3 is stored in a bucket. Before you can store data in Amazon S3, you must create a bucket.
Please refer to S3 [guides](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html) for instructions.

## Azure

### Login to Azure

Login to [Azure](Azure: https://portal.azure.com/)

### Set Credentials

First, install the Azure CLI (`pip install azure-cli azure-identity`) then login using (`az login`).

Then set the subscription to use from the command line (`az account set -s <subscription_id>`) on your working machine.

Once the Azure CLI is configured to manage resources on your Azure account, you should be ready to launch your cluster. 

### Configuring Cloud Storage

## GCP

### Login to GCP

Login to [GCP](https://console.cloud.google.com/)

### Credentials

You need to configure or log into your Cloud account to gain access to your cloud provider API.

Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable as described in
[the GCP docs](https://cloud.google.com/docs/authentication/getting-started) on your working machine.

After created a service account key, A JSON file should be safely downloaded and kept by you.

### Configuring Cloud Storage

If you do not already have a GCS bucket, create one and configure its permission for your service account.
More details, please refer to [gcs bucket guide](../GettingStarted/gcs-bucket.md).

