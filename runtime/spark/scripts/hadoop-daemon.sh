#!/bin/bash

if [ ! -n "${HADOOP_HOME}" ]; then
  echo "HADOOP_HOME environment variable is not set."
  exit 1
fi

case "$1" in
  format-cluster)
    $HADOOP_HOME/bin/hdfs namenode -format
    ;;
  start-head)
    $HADOOP_HOME/bin/hdfs --daemon start namenode
    $HADOOP_HOME/bin/hdfs --daemon start secondarynamenode
    $HADOOP_HOME/bin/yarn --daemon start resourcemanager
    ;;
  stop-head)
    $HADOOP_HOME/bin/hdfs --daemon stop namenode
    $HADOOP_HOME/bin/hdfs --daemon stop secondarynamenode
    $HADOOP_HOME/bin/yarn --daemon stop resourcemanager
    ;;
  start-worker)
    $HADOOP_HOME/bin/hdfs --daemon start datanode
    $HADOOP_HOME/bin/yarn --daemon start nodemanager
    ;;
  stop-worker)
    $HADOOP_HOME/bin/hdfs --daemon stop datanode
    $HADOOP_HOME/bin/yarn --daemon stop nodemanager
    ;;
  -h|--help)
    echo "Usage: $0 format-cluster|start-head|stop-head|start-worker|stop-worker" >&2
    ;;
  *)
    echo "Usage: $0 format-cluster|start-head|stop-head|start-worker|stop-worker" >&2
    ;;
esac