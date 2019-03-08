#!/usr/bin/env python3

import optparse
import os
import time

usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage=usage)

parser.add_option("-r", "--r-version", action="store", default="3.5.1",
                  dest="r_version", help="R version [default: %default]")
parser.add_option("-k", "--key-path", action="store", dest="key_path",
                  help="Path to the AWS key")
parser.add_option("-a", "--action", action="store", dest="action",
                  default="build_r", type="choice",
                  choices=("build_r", "create_ami"),
                  help="build R archive or create AMI [default: %default; choices: build_r, create_ami]")
parser.add_option("-t", "--terminate", action="store", dest="terminate",
                  default=True, help="terminate instance [default: %default]")
parser.add_option("-i", "--instance-type", action="store", dest="instance_type",
                  default="t2.micro",
                  help="instance type [default: %default]")
parser.add_option("-n", "--name-ami", action="store", dest="ami_name", help="name of the created AMI image (required only if --action=create_ami)")

(options, args) = parser.parse_args()

# Making sure all mandatory options appeared.
mandatories = ['key_path']
for m in mandatories:
    if not options.__dict__[m]:
        print(m + " option is missing\n")
        parser.print_help()
        exit(-1)

if options.action == "create_ami":
    existing_ami_name = os.popen("aws ec2 describe-images --filters \'Name=name,Values=" + options.ami_name + "\' --query 'Images[0]' --output text").read().strip()
    if existing_ami_name != "None":
        print("AMI name not available")
        exit(-1)

key_name = options.key_path[::-1].split("/", 1)[0].split(".", 1)[1][::-1]

ami_id = os.popen("aws ec2 describe-images --filters 'Name=name,Values=amzn-ami-hvm-2017.03.1.20170812-x86_64-gp2' --query 'Images[0].ImageId'").read().strip()

print("Instance setup")
my_server_id = os.popen(
    "aws ec2 run-instances --image-id " + ami_id + " --count 1 --instance-type " + \
    options.instance_type + \
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

print("Installing R")

keys = os.popen("ssh-keyscan -T 240 -H " + my_server_ip).read()

with open(os.path.expanduser("~/.ssh/known_hosts"), "a") as file:
    file.write(keys)

os.system(
    "scp -i " + options.key_path + " build_r.sh ec2-user@" + my_server_ip + ":/home/ec2-user/"
)
os.system(
    "ssh -i " + options.key_path + " ec2-user@" + my_server_ip + " 'chmod +x build_r.sh'"
)
os.system(
    "ssh -i " + options.key_path + " ec2-user@" + my_server_ip + " './build_r.sh '" + options.r_version
)

if options.action == "build_r":
    os.system(
        "scp -i " + options.key_path + " ec2-user@" + my_server_ip + ":/opt/R/R.zip ."
    )
elif options.action == "create_ami":
    r_lambda_ami_id = os.popen(
        "aws ec2 create-image --instance-id " + \
        my_server_id + \
        " --name " + \
        options.ami_name + \
        " --description 'Lambda AMI with R' --query 'ImageId' --output text"
    ).read().strip()
    ami_state = os.popen(
        "aws ec2 describe-images --image-id " + r_lambda_ami_id + " --query 'Images[0].State' --output text"
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

if options.terminate == True:
    os.system(
        "aws ec2 terminate-instances --instance-ids " + my_server_id
    )
