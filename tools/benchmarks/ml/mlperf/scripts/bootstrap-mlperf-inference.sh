#!/usr/bin/env bash

args=$(getopt -a -o h::p: -l head:: -- "$@")
eval set -- "${args}"

while true
do
    case "$1" in
    --head)
        IS_HEAD_NODE=true
        ;;
    --)
        shift
        break
        ;;
    esac
    shift
done

function clone_mlperf() {
    source ~/.bashrc
    sudo apt-get update -y
    sudo apt-get install -y git
    export USER_HOME=/home/$(whoami)
    BENCHMARK_TOOL_HOME=$USER_HOME/runtime/benchmark-tools
    MLPERF_HOME=$BENCHMARK_TOOL_HOME/mlperf
    MLPERF_INFERENCE_HOME=$MLPERF_HOME/inference
    MLPERF_TRAINING_HOME=$MLPERF_HOME/training
    mkdir -p $BENCHMARK_TOOL_HOME
    cd $MLPERF_HOME
    # TODO: whether select a tag to clone
    git clone --recurse-submodules https://github.com/mlcommons/training.git
    git clone --recurse-submodules https://github.com/mlcommons/inference.git
    sudo chown $(whoami):$(whoami) -R $BENCHMARK_TOOL_HOME
}

function install_tools() {
    # Install Cmake, GCC 9.0
    sudo apt-get install cmake -y
    sudo apt-get install gcc-9 g++-9 -y
#    # For RNN-T
#    sudo DEBIAN_FRONTEND=noninteractive apt-get -qq install -y sox libsndfile1 libsndfile1-dev python-pybind11
}

function install_libaries() {
    pip -qq install "git+https://github.com/mlperf/logging.git@1.0.0"
#    # For DLRM
#    pip -qq install opencv-python-headless onnx onnxruntime pydot torchvi
#    # For RNNT
#    pip -qq install pybind11==2.2
}

# Install MLPerf loadgen
function install_mlperf_loadgen() {
    cd MLPERF_INFERENCE_HOME/loadgen
    CFLAGS="-std=c++14" python setup.py install
}

clone_mlperf
install_tools
install_libaries
install_mlperf_loadgen
