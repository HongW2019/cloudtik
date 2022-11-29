#!/bin/bash

# MLPerf repo
cd $HOME
mkdir ./mlcommons && cd ./mlcommons
git clone --recurse-submodules https://github.com/mlcommons/training.git
git clone --recurse-submodules https://github.com/mlcommons/inference.git
export DLRM_DIR=$HOME/mlcommons/training/recommendation/dlrm

# Download model
cd $HOME/mlcommons/inference/recommendation
mkdir ./model && cd ./model
wget https://dlrm.s3-us-west-1.amazonaws.com/models/tb0875_10M.pt
mv tb0875_10M.pt dlrm_terabyte.pytorch

# Download datasets
cd $HOME/mlcommons/inference/recommendation
mkdir ./criteo && cd ./criteo
gsutil cp gs://cloudtik-dev/mlperf/dataset/train.txt.zip .
unzip train.txt.zip

export MODEL_DIR=$HOME/mlcommons/inference/recommendation/model
export DATA_DIR=$HOME/mlcommons/inference/recommendation/criteo
export DLRM_DIR=$HOME/mlcommons/training/recommendation/dlrm

# cd $HOME/mlcommons/inference/recommendation/dlrm/pytorch
# ./run_local.sh pytorch dlrm kaggle cpu --scenario Offline --samples-to-aggregate-fix=2048 --max-batchsize=2048
