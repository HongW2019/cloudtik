# Login to Cloud

- [AWS](#AWS)
- [Azure](#Azure)
- [GCP](#GCP)

## AWS

### Login to AWS

After created an AWS account, Login to [AWS](https://console.aws.amazon.com/)

### Authentication to boto

First, install boto (`pip install boto3`) and configure your AWS credentials in `~/.aws/credentials` as described in 
the [boto docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) on your working machine.

Once boto is configured to manage resources on your AWS account, then you can use cluster config yaml to launch cluster with CloudTik.

### Creating a bucket

Every object in Amazon S3 is stored in a bucket. Before you can store data in Amazon S3, you must create a bucket.
Please refer to S3 [guides](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html) for instructions.

## Azure

### Login to Azure

After created an Azure account, Login to [Azure](https://portal.azure.com/) to get subscription for your account.

### Authentication to Azure CLI

First, install the Azure CLI (`pip install azure-cli azure-identity`) then login using (`az login`).

Then set the subscription to use from the command line (`az account set -s <subscription_id>`) on your working machine.

Once the Azure CLI is configured to manage resources on your Azure account, then you can use cluster config yaml to
launch cluster with CloudTik.


### Configuring Cloud Storage

Create an Azure Storage Account if you don't have one.

Azure **Blob storage** or **Data Lake Storage Gen2** are both supported by CloudTik. Please refer to Azure related 
[guides](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal) for details.

## GCP

### Login to GCP

After created an GCP account, Login to [GCP](https://console.cloud.google.com/).

### Authentication to GCP API

Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable as described in
[the GCP docs](https://cloud.google.com/docs/authentication/getting-started) on your working machine.

After created a service account key, A JSON file should be safely downloaded and kept by you.

### Creating a GCP Project

Create a GCP Project with your GCP account.

### Configuring Cloud Storage

If you do not already have a GCS bucket, create one and configure its permission for your service account.
More details, please refer to [gcs bucket guide](../GettingStarted/gcs-bucket.md).

