#!/bin/sh

python make_urdf.py ~/ws_moveit/src/duckietown_description/urdf/duckiebot.urdf ~/ws_moveit/src/duckietown_description/urdf/ducks.urdf ~/ws_moveit/src/ducks/

roslaunch ducks planning_context.launch load_robot_description:=true &

roslaunch ducks move_group.launch &

