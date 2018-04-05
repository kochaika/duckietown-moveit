#!/usr/bin/env python

import sys
import argparse
import logging
import copy
import os
import yaml
import _elementtree
from xml.dom import minidom
from urdf_parser_py.urdf import *

logging.basicConfig(level=logging.DEBUG)
robot_name = "duckiebot"
robot_count = 2
robot_base_joint_type = "planar"
robot_world_joint_type = "floating"

parser = argparse.ArgumentParser(usage='Usage')
parser.add_argument('urdf_in', type=argparse.FileType('r'),
                    default=None, help='input urdf file of one robot')
parser.add_argument('urdf_out', type=argparse.FileType('w'),
                    default=None, help='output urdf file of group of robots')
parser.add_argument('out_pkg',
                    default=None, help='package with moveit description of generated group of robots')

args = parser.parse_args()

if not args.urdf_in is None:
    robot = URDF.from_xml_string(args.urdf_in.read())
else:
    print ("No urdf description found")
    exit(1)
if not os.path.exists(args.out_pkg):
    print ("Out package do not exists!")
    exit(1)
if len(robot.links) == 0:
    print("No robot links found!")
    exit(1)
elif len(robot.links) > 1:
    print("Too many robot links found!")
    exit(1)

# logging.debug("robot_link:=================\n" + str(robot_link ))
# logging.debug("============================\n")

#for .urdf
robot_link = robot.link_map.values()[0]
base_link = Link("base_link")
robots = Robot(robot_name)
robots.add_link(base_link)

# for fake_controllers.yaml
controller_list = []
fake_all_controller = {'joints': [], 'name': 'fake_all_controller'}
controller_list.append(fake_all_controller)

# for .srdf
root = _elementtree.Element('robot', {'name':robot_name})
virtual_joint = _elementtree.SubElement(root, 'virtual_joint', {'name': "virtual_joint",
                                                                'type':'planar',
                                                                'parent_frame':'odom_combined',
                                                                'child_link':'base_link'})
group_all = _elementtree.SubElement(root, 'group', {'name': "all"})

# for ompl_planning.yaml
with open("planner_configs.yaml", 'r') as planner_configs:
    ompl_planning = yaml.load(planner_configs)
    ompl_planning_robot = ompl_planning.pop('robot')

for i in range(robot_count):
    #for .urdf
    cur_robot_name = "r" + str(i)
    cur_robot_base_link = Link(cur_robot_name + "_base_link")
    cur_robot_link = copy.copy(robot_link)
    cur_robot_link.name = cur_robot_name
    robots.add_link(cur_robot_base_link)
    robots.add_link(cur_robot_link)

    cur_robot_base_joint = Joint(cur_robot_name + "_base_joint", parent=cur_robot_base_link.name,
                                 child=cur_robot_link.name, joint_type=robot_base_joint_type)
    cur_robot_world_joint = Joint(cur_robot_name + "_world_joint", parent=base_link.name,
                                  child=cur_robot_base_link.name, joint_type=robot_world_joint_type)
    cur_robot_world_joint.origin = Pose([0, 0 + 0.25*i, 0.0],[0, 0, 0])
    robots.add_joint(cur_robot_base_joint)
    robots.add_joint(cur_robot_world_joint)

    # for fake_controllers.yaml
    controller_list.append(
        {'name': 'fake_' + cur_robot_name + '_controller', 'joints': [cur_robot_name + "_base_joint"]})
    fake_all_controller['joints'].append(cur_robot_name + "_base_joint")

    # for .srdf
    cur_group = _elementtree.SubElement(root, 'group', {'name': cur_robot_name})
    cur_link = _elementtree.SubElement(cur_group, 'link', {'name': cur_robot_name})
    cur_joint = _elementtree.SubElement(cur_group, 'joint', {'name': cur_robot_name + "_base_joint"})
    cur_group = _elementtree.SubElement(group_all, 'group', {'name': cur_robot_name})

    # for ompl_planning.yaml
    ompl_planning[cur_robot_name] = copy.deepcopy(ompl_planning_robot)

# for .srdf
s = _elementtree.tostring(root, encoding="us-ascii", method="xml")
s = minidom.parseString(s)
s = s.toprettyxml(indent="  ")
with open(os.path.abspath(args.out_pkg)+"/config/duckiebot.srdf", 'w') as out_file:
    out_file.write(s)

# for ompl_planning.yaml
ompl_planning['all'] = copy.deepcopy(ompl_planning_robot)
with open(os.path.abspath(args.out_pkg)+"/config/ompl_planning.yaml", 'w') as out_file:
    out_file.write(yaml.dump(ompl_planning, default_flow_style=False))

args.urdf_out.write(robots.to_xml_string())

with open(os.path.abspath(args.out_pkg)+"/config/fake_controllers.yaml", 'w') as out_file:
    out_file.write(yaml.dump({'controller_list': controller_list}, default_flow_style=False))
