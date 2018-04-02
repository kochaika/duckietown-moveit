#!/usr/bin/env python

import sys
import argparse
import logging
import copy
from urdf_parser_py.urdf import *

logging.basicConfig(level=logging.DEBUG)
robot_name = "robots"
robot_count = 3
robot_base_joint_type = "planar"
robot_world_joint_type = "floating"

parser = argparse.ArgumentParser(usage='Usage')
parser.add_argument('in_file', type=argparse.FileType('r'),
                    default=None, help='input file')
parser.add_argument('out_file', type=argparse.FileType('w'),
                    default=None, help='out file')

args = parser.parse_args()

if args.in_file is None:
    robot = URDF.from_parameter_server()
else:
    robot = URDF.from_xml_string(args.in_file.read())

if len(robot.links) == 0:
    print("No robot links found!")
    exit(1)
elif len(robot.links) > 1:
    print("Too many robot links found!")
    exit(1)

#robot_link = Link(robot.links[0])
robot_link = robot.link_map.values()[0]
#logging.debug("robot_link:=================\n" + str(robot_link ))
#logging.debug("============================\n")

base_link = Link("base_link")
robots = Robot(robot_name)
robots.add_link(base_link)

for i in range(robot_count):
    cur_robot_name = "r" + str(i)
    cur_robot_base_link = Link (cur_robot_name + "_base_link")
    cur_robot_link = copy.copy(robot_link)
    cur_robot_link.name = cur_robot_name
    robots.add_link(cur_robot_base_link)
    robots.add_link(cur_robot_link)

    cur_robot_base_joint = Joint(cur_robot_name+"_base_joint", parent=cur_robot_base_link.name, child=cur_robot_link.name, joint_type=robot_base_joint_type)
    cur_robot_world_joint = Joint(cur_robot_name+"_world_joint", parent=base_link.name, child=cur_robot_base_link.name, joint_type=robot_world_joint_type)
    robots.add_joint(cur_robot_base_joint)
    robots.add_joint(cur_robot_world_joint)

print("===============================")


print(robots.to_xml_string())

if args.out_file is not None:
    args.out_file.write(robots.to_xml_string())

