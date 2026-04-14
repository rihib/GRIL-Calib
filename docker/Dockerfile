# Author: Tae Young Kim
# email: tyoung96@yonsei.ac.kr

FROM ros:noetic-ros-base

# Install PCL & Eigen & Ceres & essential libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    cmake libeigen3-dev libpcl-dev \
    ros-noetic-rviz ros-noetic-pcl-ros ros-noetic-eigen-conversions \
    libatlas-base-dev libgoogle-glog-dev libsuitesparse-dev libceres-dev wget \
    ros-noetic-jsk-recognition ros-noetic-jsk-common-msgs ros-noetic-jsk-rviz-plugins \
    ros-noetic-jsk-recognition-msgs \
    ros-noetic-image-transport-plugins \
    python3-pip python3-tk python3-matplotlib git \
    && rm -rf /var/lib/apt/lists/*

# Install Livox SDK
WORKDIR /root/thirdParty
RUN git clone https://github.com/Livox-SDK/Livox-SDK.git \
    && cd Livox-SDK/build && cmake .. && make -j$(nproc) && make install \
    && rm -rf /root/thirdParty/Livox-SDK

# Install livox driver
WORKDIR /root/livox_ws/src
RUN wget -q https://github.com/Livox-SDK/livox_ros_driver/archive/refs/tags/v2.6.0.tar.gz \
    && tar zxf v2.6.0.tar.gz && rm -f v2.6.0.tar.gz

RUN /bin/bash -c '. /opt/ros/noetic/setup.bash; catkin_init_workspace'

WORKDIR /root/livox_ws
RUN /bin/bash -c 'source /opt/ros/noetic/setup.bash && catkin_make'

WORKDIR /root/catkin_ws/

# Load ROS environment at each run
COPY ./ros_entrypoint.sh /
RUN chmod 755 /ros_entrypoint.sh
ENTRYPOINT ["/ros_entrypoint.sh"]

CMD ["bash"]
