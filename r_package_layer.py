#!/usr/bin/env python3

import optparse
import os
import time

usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage=usage)

parser.add_option("-k", "--key-path", action="store", dest="key_path",
                  help="Path to the AWS key")
parser.add_option("-m", "--ami-id", action="store", dest="ami_id",
                  help="id of the R Lambda AMI")
parser.add_option("-p", "--package", action="store", dest="packages",
                  help="R packages")
parser.add_option("-t", "--terminate", action="store", dest="terminate",
                  default=False, help="terminate instance [default: %default]")
parser.add_option("-i", "--instance-type", action="store", dest="instance_type",
                  default="t2.micro",
                  help="instance type [default: %default]")

(options, args) = parser.parse_args()

# Making sure all mandatory options appeared.
mandatories = ['key_path', 'ami_id', 'packages']
for m in mandatories:
    if not options.__dict__[m]:
        print(m + " option is missing\n")
        parser.print_help()
        exit(-1)

key_name = options.key_path[::-1].split("/", 1)[0].split(".", 1)[1][::-1]

print("Instance setup")
my_server_id = os.popen(
    "aws ec2 run-instances --image-id " + \
    options.ami_id + \
    " --count 1 --instance-type " + \
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

print("Installing R packages")

keys = os.popen("ssh-keyscan -T 240 -H " + my_server_ip).read()

with open(os.path.expanduser("~/.ssh/known_hosts"), "a") as file:
    file.write(keys)

os.system(
    "ssh -i " + options.key_path + " ec2-user@" + my_server_ip + " 'mkdir -p /opt/R/new_library/R/library'"
)

packages = options.packages.replace(',', '').split()

if os.path.isfile("tmp.R"):
    os.remove("tmp.R")

with open("tmp.R", "a") as file:
    file.write("chooseCRANmirror(graphics=FALSE, ind=34)\n")
    for package in packages:
        file.write("install.packages(\'" + package + "\', lib = \'/opt/R/new_library/R/library\')\n")

os.system(
    "scp -i " + options.key_path + " tmp.R ec2-user@" + my_server_ip + ":/home/ec2-user/"
)

os.system(
    "ssh -i " + options.key_path + " ec2-user@" + my_server_ip + " '/opt/R/bin/Rscript /home/ec2-user/tmp.R'"
)

os.remove("tmp.R")

os.system(
    "ssh -i " + options.key_path + " ec2-user@" + my_server_ip + " 'cd /opt/R/new_library && zip -r packages.zip R/'"
)

os.system(
    "scp -i " + options.key_path + " ec2-user@" + my_server_ip + ":/opt/R/new_library/packages.zip ."
)

if options.terminate == True:
    os.system(
        "aws ec2 terminate-instances --instance-ids " + my_server_id
    )
