FROM nvidia/cuda:9.0-devel-ubuntu16.04

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        libpng-dev \
        libssl-dev

RUN echo ''' \
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial main restricted universe multiverse \
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates main restricted universe multiverse \
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-backports main restricted universe multiverse \
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security main restricted universe multiverse \
''' > /etc/apt/sources.list

# TensorFlow version is tightly coupled to CUDA and cuDNN so it should be selected carefully
ENV TENSORFLOW_VERSION=1.12.0
ENV PYTORCH_VERSION=1.0.0
ENV CUDNN_VERSION=7.4.1.5-1+cuda9.0
ENV NCCL_VERSION=2.3.5-2+cuda9.0

ARG python=3.6
ENV PYTHON_VERSION=${python}

RUN echo 'deb http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64 /' > /etc/apt/sources.list.d/cuda.list

RUN apt-get update && apt-get install -y --no-install-recommends \
        zip \
        unzip \
        build-essential \
        cmake \
        git \
        vim \
        wget \
        ca-certificates \
        libjpeg-dev \
        libpng-dev

RUN sh -c 'wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub | apt-key add -'

RUN apt-get install -y --no-install-recommends --allow-downgrades --allow-change-held-packages \
        libcudnn7=${CUDNN_VERSION} \
        libnccl2=${NCCL_VERSION} \
        libnccl-dev=${NCCL_VERSION}

RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-${PYTHON_VERSION}
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python${PYTHON_VERSION}-venv

RUN ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python

RUN rm /usr/bin/python3 && ln -s /usr/bin/python3.6 /usr/bin/python3

RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install --upgrade setuptools

RUN pip install keras

RUN pip install easydict matplotlib IPython scikit-learn scikit-image termcolor protobuf pandas cython

RUN pip install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'

# Install TensorFlow, Keras and PyTorch
RUN pip install tensorflow-gpu==${TENSORFLOW_VERSION} keras h5py torch==${PYTORCH_VERSION} torchvision

# Install Open MPI
RUN mkdir /tmp/openmpi && \
    cd /tmp/openmpi && \
    wget https://www.open-mpi.org/software/ompi/v3.1/downloads/openmpi-3.1.2.tar.gz && \
    tar zxf openmpi-3.1.2.tar.gz && \
    cd openmpi-3.1.2 && \
    ./configure --enable-orterun-prefix-by-default && \
    make -j $(nproc) all && \
    make install && \
    ldconfig && \
    rm -rf /tmp/openmpi

# Install Horovod, temporarily using CUDA stubs
RUN ldconfig /usr/local/cuda-9.0/targets/x86_64-linux/lib/stubs && \
    HOROVOD_GPU_ALLREDUCE=NCCL HOROVOD_WITH_TENSORFLOW=1 HOROVOD_WITH_PYTORCH=1 pip install --no-cache-dir horovod && \
    ldconfig

# Create a wrapper for OpenMPI to allow running as root by default
RUN mv /usr/local/bin/mpirun /usr/local/bin/mpirun.real && \
    echo '#!/bin/bash' > /usr/local/bin/mpirun && \
    echo 'mpirun.real --allow-run-as-root "$@"' >> /usr/local/bin/mpirun && \
    chmod a+x /usr/local/bin/mpirun

# Configure OpenMPI to run good defaults:
#   --bind-to none --map-by slot --mca btl_tcp_if_exclude lo,docker0
RUN echo "hwloc_base_binding_policy = none" >> /usr/local/etc/openmpi-mca-params.conf && \
    echo "rmaps_base_mapping_policy = slot" >> /usr/local/etc/openmpi-mca-params.conf && \
    echo "btl_tcp_if_exclude = lo,docker0" >> /usr/local/etc/openmpi-mca-params.conf

# Set default NCCL parameters
RUN echo NCCL_DEBUG=INFO >> /etc/nccl.conf && \
    echo NCCL_SOCKET_IFNAME=^docker0 >> /etc/nccl.conf

# Install OpenSSH for MPI to communicate between containers
RUN apt-get install -y --no-install-recommends openssh-client openssh-server && \
    mkdir -p /var/run/sshd

# Allow OpenSSH to talk to containers without asking for confirmation
RUN cat /etc/ssh/ssh_config | grep -v StrictHostKeyChecking > /etc/ssh/ssh_config.new && \
    echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config.new && \
    mv /etc/ssh/ssh_config.new /etc/ssh/ssh_config


RUN apt-get install -y --no-install-recommends subversion && \
    svn checkout https://github.com/uber/horovod/trunk/examples && \
    rm -rf /examples/.svn

RUN sed -i 's/prohibit-password/yes/' /etc/ssh/sshd_config

RUN sh -c 'echo "123456\n123456" | passwd'

RUN echo '''TF_MODEL_RESEARCH=/root/develop/tf/tf_models/research/ \n\
export PYTHONPATH=$PYTHONPATH:$TF_MODEL_RESEARCH:$TF_MODEL_RESEARCH/slim \n\
export LD_LIBRARY_PATH=/usr/local/TensorRT-4.0.1.6/lib:/usr/local/cuda-9.0/lib64:/usr/local/cuda/extras/CUPTI/lib64:$LD_LIBRARY_PATH \n\
''' >> ~/.bashrc


# timezone
WORKDIR /app
COPY Shanghai Shanghai
RUN mkdir -p /usr/share/zoneinfo/Asia
RUN /bin/cp Shanghai /usr/share/zoneinfo/Asia/Shanghai
RUN rm -f /etc/localtime && /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone

# tensorboard

RUN echo 'export LC_ALL=C' >> ~/.bashrc

# horovod mpi

RUN sed -i 's/btl_tcp_if_exclude/#btl_tcp_if_exclude/' /usr/local/etc/openmpi-mca-params.conf

# tensorflow online
WORKDIR /root
COPY bazel-0.18.1-installer-linux-x86_64.sh bazel-0.18.1-installer-linux-x86_64.sh
RUN cd /root && ./bazel-0.18.1-installer-linux-x86_64.sh
COPY cudnn-7.4.1/cuda/include/cudnn.h cudnn.h
RUN cd /root && cp cudnn.h /usr/local/cuda-9.0/include
COPY TensorRT-4.0.1.6 TensorRT-4.0.1.6
RUN cd /root && mv TensorRT-4.0.1.6 /usr/local

WORKDIR /app
COPY protobuf-all-3.6.1.tar.gz protobuf-all-3.6.1.tar.gz
RUN tar xfz protobuf-all-3.6.1.tar.gz && \
    cd protobuf-3.6.1 && ./configure && \
    make -j"$(nproc)" && make install && \
    cd /app && rm -rf protobuf*

# tensorflow online predict example
WORKDIR /app
COPY opencv340.tar.gz opencv340.tar.gz
RUN tar xfz opencv340.tar.gz && \
   cd opencv340 && mkdir build && cd build && \
   cmake -D WITH_LIBV4L=ON \
      -D CMAKE_BUILD_TYPE=Release \
      -D BUILD_PNG=ON \
      -D BUILD_JPG=ON \
      -D WITH_TIFF=ON \
      -D WITH_CUDA=OFF \
      -D WITH_V4L=ON \
      -D WITH_FFMPEG=ON \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      .. && make -j"$(nproc)" && make install && \
      cd /app && rm -fr opencv340*

# tensorflow od, tensorpack

RUN pip install opencv-python tqdm
RUN apt install -y libsm6 libxext6
RUN apt-get install -y libfontconfig1 libxrender1
RUN echo '''export PYTHONPATH=$PYTHONPATH:~/develop/tf/tensorpack''' >> ~/.bashrc

RUN pip install contextlib2 lxml zmq tabulate msgpack msgpack_numpy

RUN apt-get install -y pkg-config libcap-dev net-tools libzmq3-dev

WORKDIR /app

RUN git clone http://github.com/seveas/python-prctl && cd python-prctl && python setup.py build && python setup.py install

WORKDIR /app

RUN git clone https://github.com/zeromq/cppzmq.git && cp cppzmq/zmq.hpp /usr/local/include
RUN export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64/stubs/ && git clone https://github.com/tensorpack/zmq_ops.git && cd zmq_ops && pip install . && python -c "from zmq_ops import dump_arrays"

RUN echo '''export TF_CUDNN_USE_AUTOTUNE=0''' >> ~/.bashrc

# pocketflow

RUN pip install docopt hdfs scipy sklearn pandas mpi4py

# HDFS
WORKDIR /app
COPY python_basics.tar.gz python_basics.tar.gz
RUN tar xfz python_basics.tar.gz --directory /root && \
    rm -f /app/python_basics.tar.gz

WORKDIR /app
COPY hadoop-2.6.5.tar.gz hadoop-2.6.5.tar.gz
RUN mkdir -p /opt/package && \
    tar -zxvf hadoop-2.6.5.tar.gz --directory /opt/package && \
    cp /root/python_basics/hadoop_configs/bj-config-new/hdfs-site.xml /opt/package/hadoop-2.6.5/etc/hadoop && \
    cp /root/python_basics/hadoop_configs/bj-config-new/core-site.xml /opt/package/hadoop-2.6.5/etc/hadoop && \
    cp /root/python_basics/hadoop_configs/bj-config-new/hadoop-env.sh /opt/package/hadoop-2.6.5/etc/hadoop && \
    cp /root/python_basics/hadoop_configs/bj-config-new/log4j.properties /opt/package/hadoop-2.6.5/etc/hadoop && \
    rm -f /app/hadoop-2.6.5.tar.gz

 # java
WORKDIR /app
COPY jdk1.8.0_181.tar.gz jdk1.8.0_181.tar.gz
RUN tar xfz jdk1.8.0_181.tar.gz --directory /opt/package && \
    rm -f /app/jdk1.8.0_181.tar.gz

WORKDIR /opt/package
RUN echo '''export JAVA_HOME=/opt/package/jdk1.8.0_181 \n\
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar \n\
export HADOOP_HOME=/opt/package/hadoop-2.6.5 \n\
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native \n\
export HADOOP_OPTS="$HADOOP_OPTS -Djava.library.path=$HADOOP_HOME/lib" \n\
export PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin \n\
''' >> ~/.bashrc


WORKDIR /app
COPY gflags-2.2.2.zip gflags-2.2.2.zip
RUN unzip gflags-2.2.2.zip && \
    cd gflags-2.2.2 && mkdir build && cd build && \
    cmake .. && make -j"$(nproc)" && make install


RUN apt-get install -y graphviz


### tf 0.2.3

RUN pip install shapely addict yacs

RUN echo '''export PYTHONPATH=$PYTHONPATH:/detection/tensorpack''' >> ~/.bashrc

RUN echo '''export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/detection/tf_detection_test/build''' >> ~/.bashrc

ENV PYTHONPATH=/detection/tensorpack:$PYTHONPATH


WORKDIR "/detection"

COPY tf_detection_test tf_detection_test

COPY tf_detection_test/run_test.py run_test.py

COPY detection-training-wrapper detection-training-wrapper
COPY tensorpack tensorpack

ENV JAVA_HOME=/opt/package/jdk1.8.0_181
ENV CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
ENV HADOOP_HOME=/opt/package/hadoop-2.6.5
ENV HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
ENV HADOOP_OPTS="$HADOOP_OPTS -Djava.library.path=$HADOOP_HOME/lib"
ENV PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin

ENV TF_CUDNN_USE_AUTOTUNE=0
ENV LD_LIBRARY_PATH=/usr/local/TensorRT-4.0.1.6/lib:/usr/local/cuda-9.0/lib64:/usr/local/cuda/extras/CUPTI/lib64:/detection/tf_detection_test/build


RUN pip install sqlalchemy mysql-connector-python pymysql

RUN pip install snakebite

RUN apt-get install -y tmux

WORKDIR "/root"
COPY .ssh /root/.ssh
COPY .tumx.conf /root/.tmux.conf

WORKDIR "/detection"

