#!/usr/bin/env python

import sys
import argparse

from urdf_parser_py.urdf import *

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

#print(robot.links[0])
robots = Robot()
robots.name = "two_robots"
robots.add_link(robot.links[0])
robots.add_link(robot.links[0])
print(robots.to_xml_string())

if args.out_file is not None:
    args.out_file.write(robots.to_xml_string())

