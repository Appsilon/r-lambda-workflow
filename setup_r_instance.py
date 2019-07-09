#!/usr/bin/env python3

import argparse
import os
import time
from library.ssh_connection import Ssh
import library.instance_handling as instance

parser = argparse.ArgumentParser()

parser.add_argument("-r", "--r-version", action="store", default="3.5.1",
                  dest="r_version", help="R version (default: %(default)s)")
parser.add_argument("-k", "--key-path", action="store", dest="key_path",
                  help="Path to the AWS key", required=True)
parser.add_argument("-a", "--action", action="store", dest="action",
                  default="build_r",
                  choices=["build_r", "create_ami"],
                  help="build R archive or create AMI (default: %(default)s; choices: build_r, create_ami)")
parser.add_argument("-t", "--terminate", action="store", dest="terminate",
                  default=True, help="terminate instance (default: %(default)s)")
parser.add_argument("-i", "--instance-type", action="store", dest="instance_type",
                  default="t2.micro",
                  help="instance type [default: %(default)s]")
parser.add_argument("-n", "--name-ami", action="store", dest="ami_name", help="name of the created AMI image (required only if --action=create_ami)")

arguments = parser.parse_args()

key_path = os.path.expanduser(arguments.key_path)
key_name = os.path.splitext(os.path.basename(key_path))[0]

if arguments.action == "create_ami":
    existing_ami_name = os.popen("aws ec2 describe-images --filters \'Name=name,Values=" + arguments.ami_name + "\' --query 'Images[0]' --output text").read().strip()
    if existing_ami_name != "None":
        print("AMI name not available")
        exit(-1)


ami_id = os.popen("aws ec2 describe-images --filters 'Name=name,Values=amzn-ami-hvm-2017.03.1.20170812-x86_64-gp2' --query 'Images[0].ImageId'").read().strip()

print("Instance setup")
my_server_ip, my_server_id = instance.setup_instance(ami_id, arguments.instance_type, key_name)

print("Connecting to server")

connection = Ssh(ip = my_server_ip, key_path = key_path)

print("Installing R")

connection.upload_file("build_r.sh", "/home/ec2-user/build_r.sh")
connection.send_command("chmod +x /home/ec2-user/build_r.sh")
connection.send_command("cd /home/ec2-user && ./build_r.sh " + arguments.r_version)

print("R installed")

if arguments.action == "build_r":
    try:
        connection.download_file("/opt/R/R.zip", "R.zip")
        print("R downloaded")
    except:
        print("")
elif arguments.action == "create_ami":
    r_lambda_ami_id = os.popen(
        f"aws ec2 create-image --instance-id {my_server_id} --name {arguments.ami_name} --description 'Lambda AMI with R' --query 'ImageId' --output text"
    ).read().strip()
    ami_state = os.popen(
        f"aws ec2 describe-images --image-id {r_lambda_ami_id} --query 'Images[0].State' --output text"
    ).read().strip()
    while ami_state != "available":
        print("Waiting for AMI")
        time.sleep(10)
        ami_state = os.popen(
            "aws ec2 describe-images --image-id " + r_lambda_ami_id + " --query 'Images[0].State' --output text"
        ).read().strip()
    print("AMI id: " + r_lambda_ami_id)
else:
    print("Not a valid action")

if arguments.terminate:
    instance.terminate_instance(my_server_id)
