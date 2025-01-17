# Common Imports
import getopt
import os
import subprocess
import sys
from distutils.version import LooseVersion


# Parse and get parameters
try:
    opts, args = getopt.getopt(sys.argv[1:], "f:b:e:")
except getopt.GetoptError:
    print("Invalid options. Support -f for storage filesystem dir, -b for batch size,  -e for epochs.")
    sys.exit(1)

param_batch_size = None
param_epochs = None
param_fsdir = None
for opt, arg in opts:
    if opt in ['-f']:
        param_fsdir = arg
    elif opt in ['-b']:
        param_batch_size = arg
    elif opt in ['-e']:
        param_epochs = arg


from cloudtik.runtime.spark.api import ThisSparkCluster
from cloudtik.runtime.ml.api import ThisMLCluster

cluster = ThisSparkCluster()

# Scale the cluster as need
cluster.scale(workers=3)

# Wait for all cluster workers to be ready
cluster.wait_for_ready(min_workers=3)

# Total worker cores
cluster_info = cluster.get_info()
total_worker_cpus = cluster_info.get("total-worker-cpus")
if not total_worker_cpus:
    total_worker_cpus = 1

default_storage = cluster.get_default_storage()
if not param_fsdir:
    param_fsdir = default_storage.get("default.storage.uri") if default_storage else None
    if not param_fsdir:
        print("Must specify storage filesystem dir using -f.")
        sys.exit(1)

ml_cluster = ThisMLCluster()
mlflow_url = ml_cluster.get_services()["mlflow"]["url"]


# Initialize SparkSession
from pyspark import SparkConf
from pyspark.sql import SparkSession

spark_conf = SparkConf().setAppName('spark-horovod-keras').set('spark.sql.shuffle.partitions', '16')
spark = SparkSession.builder.config(conf=spark_conf).getOrCreate()
conf = spark.conf


# Download MNIST dataset and upload to storage

# Download
data_url = 'https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/multiclass/mnist.bz2'
mnist_data_path = os.path.join('/tmp', 'mnist.bz2')
if not os.path.exists(mnist_data_path):
    subprocess.check_output(['wget', data_url, '-O', mnist_data_path])

# Upload to the default distributed storage
os.system("hadoop fs -mkdir /tmp")
os.system("hadoop fs -put   /tmp/mnist.bz2  /tmp")


# Feature processing

# Load to Spark dataframe
df = spark.read.format('libsvm').option('numFeatures', '784').load(mnist_data_path)

# One-hot encode labels into SparseVectors
from pyspark.ml.feature import OneHotEncoder

encoder = OneHotEncoder(inputCols=['label'],
                        outputCols=['label_vec'],
                        dropLast=False)
model = encoder.fit(df)
train_df = model.transform(df)

# Split to train/test
train_df, test_df = train_df.randomSplit([0.9, 0.1])
if train_df.rdd.getNumPartitions() < total_worker_cpus:
    train_df = train_df.repartition(total_worker_cpus)


# Define training function and Keras model
import numpy as np

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D

import horovod.spark.keras as hvd
from horovod.spark.common.backend import SparkBackend
from horovod.spark.common.store import Store

import pyspark.sql.types as T
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql.functions import udf

import mlflow

# Disable GPUs when building the model to prevent memory leaks
if LooseVersion(tf.__version__) >= LooseVersion('2.0.0'):
    # See https://github.com/tensorflow/tensorflow/issues/33168
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
else:
    keras.backend.set_session(tf.Session(config=tf.ConfigProto(device_count={'GPU': 0})))

# Set the parameters
set_num_proc = total_worker_cpus
print("Spark Backend num_proc: {}".format(set_num_proc))

set_batch_size = int(param_batch_size) if param_batch_size else 128
print("Keras Estimator batch_size: {}".format(set_batch_size))

set_epochs = int(param_epochs) if param_epochs else 1
print("Keras Estimator epochs: {}".format(set_epochs))

# Create store for data accessing
store_path = param_fsdir + "/tmp"
# AWS and GCP cloud storage authentication just work with empty storage options
# Azure cloud storage authentication needs a few options
storage_options = {}
if default_storage and "azure.storage.account" in default_storage:
    storage_options["anon"] = False
    storage_options["account_name"] = default_storage["azure.storage.account"]
store = Store.create(store_path, storage_options=storage_options)


#  Horovod distributed training
def train(learning_rate):
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3),
                     activation='relu',
                     input_shape=(28, 28, 1)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(10, activation='softmax'))

    optimizer = keras.optimizers.Adadelta(learning_rate)
    loss = keras.losses.categorical_crossentropy

    backend = SparkBackend(num_proc=set_num_proc,
                       stdout=sys.stdout, stderr=sys.stderr,
                       prefix_output_with_timestamp=True)
    keras_estimator = hvd.KerasEstimator(backend=backend,
                                         store=store,
                                         model=model,
                                         optimizer=optimizer,
                                         loss=loss,
                                         metrics=['accuracy'],
                                         feature_cols=['features'],
                                         label_cols=['label_vec'],
                                         batch_size=set_batch_size,
                                         epochs=set_epochs,
                                         verbose=1)

    keras_model = keras_estimator.fit(train_df).setOutputCols(['label_prob'])
    return keras_model


#  Hyperopt training function
def hyper_objective(learning_rate):
    keras_model = train(learning_rate)
    pred_df = keras_model.transform(test_df)
    argmax = udf(lambda v: float(np.argmax(v)), returnType=T.DoubleType())
    pred_df = pred_df.withColumn('label_pred', argmax(pred_df.label_prob))

    evaluator = MulticlassClassificationEvaluator(predictionCol='label_pred', labelCol='label', metricName='accuracy')
    accuracy = evaluator.evaluate(pred_df)
    print('Test accuracy:', accuracy)

    with mlflow.start_run():
      mlflow.log_metric("learning_rate", learning_rate)
      mlflow.log_metric("loss", 1-accuracy)
    return {'loss': 1-accuracy, 'status': STATUS_OK}


# Do a super parameter tuning with hyperopt

from hyperopt import fmin, tpe, hp, STATUS_OK, Trials

search_space = hp.uniform('learning_rate', 0, 1)
mlflow.set_tracking_uri(mlflow_url)
mlflow.set_experiment("MNIST: Spark + Horovod + Hyperopt")
argmin = fmin(
    fn=hyper_objective,
    space=search_space,
    algo=tpe.suggest,
    max_evals=16)
print("Best value found: ", argmin)


# Train final model with the best parameters
best_model = train(argmin.get('learning_rate'))
metadata = best_model._get_metadata()
floatx = best_model._get_floatx()
mlflow.keras.log_model(best_model.getModel(), "keras-mnist-model", registered_model_name="keras-mnist-model-reg")


# Load the model from MLflow and run a transformation
model_uri = "models:/keras-mnist-model-reg/1"
loaded_model = mlflow.keras.load_model(model_uri)

hvd_keras_model = hvd.KerasModel(model=loaded_model,
                                 feature_columns=['features'],
                                 label_columns=['label_vec'],
                                 _floatx=floatx,
                                 _metadata=metadata).setOutputCols(['label_prob'])

pred_df = hvd_keras_model.transform(test_df)
argmax = udf(lambda v: float(np.argmax(v)), returnType=T.DoubleType())
pred_df = pred_df.withColumn('label_pred', argmax(pred_df.label_prob))

evaluator = MulticlassClassificationEvaluator(predictionCol='label_pred', labelCol='label', metricName='accuracy')
accuracy = evaluator.evaluate(pred_df)
print('Test accuracy:', accuracy)

pred_df = pred_df.sampleBy('label', fractions={0.0: 0.1, 1.0: 0.1, 2.0: 0.1, 3.0: 0.1, 4.0: 0.1, 5.0: 0.1, 6.0: 0.1, 7.0: 0.1, 8.0: 0.1, 9.0: 0.1})
pred_df.show(150)

# Clean up
spark.stop()
