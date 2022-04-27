#!/bin/bash

export USER_HOME=/home/$(whoami)
export BENCHMARK_TOOL_HOME=$USER_HOME/runtime/benchmark-tools
[ ! -d "$BENCHMARK_TOOL_HOME" ] && mkdir -p "$BENCHMARK_TOOL_HOME"
oap_install_dir=$BENCHMARK_TOOL_HOME/oap


##  Install oap by Conda

conda create -p "${oap_install_dir}" -c conda-forge -c intel -y oap=1.3.1.dataproc20
