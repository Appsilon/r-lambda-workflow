#!/usr/bin/env python3

import argparse
import os
import time
from library.ssh_connection import Ssh

parser = argparse.ArgumentParser()

parser.add_argument("-k", "--key-path", action="store", dest="key_path",
                  help="Path to the AWS key", required=True)
parser.add_argument("-m", "--ami-id", action="store", dest="ami_id",
                  help="id of the R Lambda AMI", required=True)
parser.add_argument("-p", "--package", action="store", dest="packages",
                  help="R packages", required=True)
parser.add_argument("-t", "--terminate", action="store", dest="terminate",
                  default=True, help="terminate instance (default: %(default)s)")
parser.add_argument("-i", "--instance-type", action="store", dest="instance_type",
                  default="t2.micro",
                  help="instance type (default: %(default)s)")

arguments = parser.parse_args()

key_path = os.path.expanduser(arguments.key_path)
key_name = os.path.splitext(os.path.basename(key_path))[0]

print("Instance setup")
my_server_id = os.popen(
    "aws ec2 run-instances --image-id " + \
    arguments.ami_id + \
    " --count 1 --instance-type " + \
    arguments.instance_type + \
    " --key-name " + key_name + \
    " --query 'Instances[0].InstanceId' --output text"
).read().strip()

my_server_status = os.popen(
    "aws ec2 describe-instance-status --instance-id " + \
    my_server_id + \
    " --query 'InstanceStatuses[0].SystemStatus.Status' --output text --output text"
).read().strip()

while my_server_status != "ok":
    print("Waiting for instance")
    time.sleep(10)
    my_server_status = os.popen(
        "aws ec2 describe-instance-status --instance-id " + \
        my_server_id + \
        " --query 'InstanceStatuses[0].SystemStatus.Status' --output text --output text"
    ).read().strip()

my_server_ip = os.popen(
    "aws ec2 describe-instances --instance-id " + \
    my_server_id + \
    " --query 'Reservations[0].Instances[0].PublicIpAddress' --output text"
).read().strip()

print("Connecting to server")

connection = Ssh(ip = my_server_ip, key_path = key_path)

print("Installing R packages")

connection.send_command("mkdir -p /opt/R/new_library/R/library")

packages = arguments.packages.replace(',', '').split()

if os.path.isfile("tmp.R"):
    os.remove("tmp.R")

with open("tmp.R", "a") as file:
    file.write("chooseCRANmirror(graphics=FALSE, ind=34)\n")
    for package in packages:
        file.write("install.packages(\'" + package + "\', lib = \'/opt/R/new_library/R/library\')\n")

connection.upload_file("tmp.R", "/home/ec2-user/tmp.R")
connection.send_command("/opt/R/bin/Rscript /home/ec2-user/tmp.R")

os.remove("tmp.R")

print("Download packages")

connection.send_command("cd /opt/R/new_library && zip -r -q packages.zip R/")
connection.download_file("/opt/R/new_library/packages.zip", "packages.zip")

if arguments.terminate == True:
    os.system(
        "aws ec2 terminate-instances --instance-ids " + my_server_id
    )
