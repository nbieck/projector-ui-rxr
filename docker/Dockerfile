FROM nvidia/cudagl:10.2-base-ubuntu18.04
# Distribution of ROS2
ARG distro="dashing"

WORKDIR /

# Install necessary software for the installation of ROS2
RUN apt-get update && apt-get install -y \
                      locales \
                      curl \
                      gnupg2 \
                      lsb-release \
                      python3 \
                      python3-dev \
                      python3-pip \
                      python3-setuptools \
                      build-essential \
                      libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*rm

# install packages for opencv python
RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install scikit-build numpy
RUN python3 -m pip install --upgrade pip setuptools
RUN python3 -m pip install opencv-python

# Add key
RUN curl http://repo.ros2.org/repos.key | apt-key add -
RUN sh -c 'echo "deb [arch=amd64,arm64] http:packages.ros.org/ros2/ubuntu `lsb_release -cs` main" > /etc/apt/sources.list.d/ros2-latest.list' \ 
 && apt update

# Specify the distribution of ROS2
ENV ROS_DISTRO $distro
ENV DEBIAN_FRONTEND=noninteractive

# Install ROS2
RUN apt install -y ros-$ROS_DISTRO-desktop \
                python3-colcon-common-extensions \
                python3-rosdep \
                python3-argcomplete \
    && rm -rf /var/lib/apt/lists/*rm


