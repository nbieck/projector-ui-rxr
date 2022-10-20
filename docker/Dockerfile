# Dockerfile for ROS2 on Ubuntu 18.04
# The installation step follows the instruction in "ROS2ではじめよう 次世代ロボットプログラミング" by Yutaka Kondo
# Author: ShigemichiMatsuzaki
# Date  : 2019/9/21

#FROM ubuntu:18.04
# FROM nvidia/opengl:1.0-glvnd-runtime-ubuntu18.04
FROM nvidia/cudagl:10.2-base-ubuntu18.04
# Distribution of ROS2
ARG distro="dashing"

WORKDIR /root

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
    
# Initialize rosdep
RUN rosdep init && rosdep update

RUN sudo apt-get install -y ros-dashing-cv-bridge ros-dashing-librealsense2 ros-dashing-message-filters ros-dashing-image-transport
RUN sudo apt-get install -y libssl-dev libusb-1.0-0-dev pkg-config libgtk-3-dev
RUN sudo apt-get install -y libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev
RUN sudo apt-get install -y ros-dashing-realsense-camera-msgs ros-dashing-realsense-ros2-camera
RUN apt install ros-eloquent-image-tools -y

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nano \
    vim \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Setup scripts
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /root/.bashrc

# Set the entry point
COPY ./docker/ros_entrypoint.sh /
RUN chmod +x /ros_entrypoint.sh
RUN sed -i -e 's/\r$//' /ros_entrypoint.sh

RUN ls

COPY ./workspace/ /

#ENTRYPOINT ["/ros_entrypoint.sh"]
#CMD ["bash"]
