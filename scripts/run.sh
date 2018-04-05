#!/bin/sh

python make_urdf.py ../catkin_ws/src/duckietown_description/urdf/duckiebot.urdf ../catkin_ws/src/duckietown_description/urdf/ducks.urdf ../catkin_ws/src/ducks/

roslaunch ducks planning_context.launch load_robot_description:=true &

roslaunch ducks move_group.launch &

