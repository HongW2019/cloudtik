#!/bin/bash

export USER_HOME=/home/$(whoami)
export BENCHMARK_TOOL_HOME=$USER_HOME/runtime/benchmark-tools
mkdir -p "$BENCHMARK_TOOL_HOME"
oap_install_dir=$BENCHMARK_TOOL_HOME/oap


## Step 2: conda install oap

which conda && conda create -p "${oap_install_dir}" -c conda-forge -c intel -y oap=1.3.1.dataproc20
