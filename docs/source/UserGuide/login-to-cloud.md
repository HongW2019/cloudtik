# Login to Cloud

- [AWS](#aws)
- [Azure](#azure)
- [GCP](#gcp)

## AWS

### AWS Account

Create an AWS account if you don't have one, then login to [AWS](https://console.aws.amazon.com/).

Please refer to related [AWS documentation](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)
for instructions.

### Authentication to AWS CLI

Install or update the AWS CLI on your working machine with the following commands.

```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws configure
```
Then fill out your *AWS Access Key ID*, *AWS Secret Access Key* and *Default region name* to the command prompt.

Please refer to [AWS docs](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) for more details.

### Creating a bucket

Every object in Amazon S3 is stored in a bucket. Before you can store data in Amazon S3, you must create a bucket.
Please refer to S3 [guides](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html) for instructions.

## Azure

### Azure Account

Create an Azure account if you don't have one, then login to [Microsoft Azure portal](https://portal.azure.com/) to get
[Subscription ID](https://docs.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id#find-your-azure-subscription)
of your account.

Please refer to related [Azure documentation](https://docs.microsoft.com/en-us/learn/modules/create-an-azure-account/)
for instructions.

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

### Google Cloud Account

Created a Google Cloud account if you don't have one, then login to [GCP](https://console.cloud.google.com/).

Please refer to related [GCP documentation](https://cloud.google.com/apigee/docs/hybrid/v1.3/precog-gcpaccount)
for instructions.

### Creating a Google Cloud Project

Google Cloud projects form the basis for creating, enabling, and using all Google Cloud services.
Create a project within your Google Cloud account. 

Please refer to 
[Google Cloud Guide](https://cloud.google.com/resource-manager/docs/creating-managing-projects) for instructions.

### Authentication calls to Google Cloud APIs.

Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable as described in
[the GCP docs](https://cloud.google.com/docs/authentication/getting-started) on your working machine.

After created a service account key, A JSON file should be safely downloaded and kept by you.

### Configuring Cloud Storage

If you do not already have a GCS bucket, create one and configure its permission for your service account.
More details, please refer to [gcs bucket guide](../GettingStarted/gcs-bucket.md).

