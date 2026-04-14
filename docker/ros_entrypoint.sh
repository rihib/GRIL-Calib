#!/bin/bash
 
set -e

# Ros build
source "/opt/ros/noetic/setup.bash"
source "/root/livox_ws/devel/setup.bash"


# Libray install if you want

echo "================Gril-Calib Docker Env Ready================"

mkdir -p /root/catkin_ws/src/Log /root/catkin_ws/src/result
cd /root/catkin_ws

exec "$@"
