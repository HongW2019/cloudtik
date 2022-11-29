ARG BASE_IMAGE="nightly"
FROM cloudtik/spark-runtime:"$BASE_IMAGE"

RUN sudo apt-get update -y \
    && sudo apt-get install -y \
        cmake \
        g++-9 \
        build-essential sox libsndfile1-dev \
    # Clean up
    && sudo rm -rf /var/lib/apt/lists/* \
    && sudo apt-get clean

WORKDIR /home/cloudtik/
COPY requirements.txt /tmp/requirements.txt
RUN export PATH="$HOME/anaconda3/envs/$CLOUDTIK_ENV/bin:$PATH" \
    && pip install -r /tmp/requirements.txt \
    && sudo rm /tmp/requirements.txt \
    && pip install torch==1.12.0 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu \
    && export CXX=/usr/bin/g++-9 \
    && HOROVOD_WITH_PYTORCH=1 HOROVOD_WITH_TENSORFLOW=1 HOROVOD_WITH_MXNET=1 HOROVOD_WITH_GLOO=1  pip install horovod[all-frameworks]==0.25.0

# MLPerf dependencies
RUN pip install opencv-python-headless onnx onnxruntime pydot torchviz pybind11 \
    && pip install "git+https://github.com/mlperf/logging.git@1.0.0"

# MLPerf inference
RUN cd /tmp && \
    git clone --recurse-submodules https://github.com/mlcommons/inference && \
    # build and install the loadgen
    cd inference/loadgen && \
    CFLAGS="-std=c++14" python setup.py install
