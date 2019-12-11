#!/usr/bin/env python3

import argparse
import os
from library.ssh_connection import Ssh
import library.instance_handling as instance
import logging


def concatenate_list_data(list):
    result= ''
    for element in list:
        result += str(element)
    return result

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)

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

logger.info("Instance setup")
my_server_ip, my_server_id = instance.setup_instance(arguments.ami_id, arguments.instance_type, key_name)

logger.info("Connecting to server")

connection = Ssh(ip = my_server_ip, key_path = key_path)

logger.info("Installing R packages")

connection.send_command("mkdir -p /opt/R/new_library/R/library")

packages = arguments.packages.replace(',', '').split()

if os.path.isfile("tmp.R"):
    os.remove("tmp.R")

with open("tmp.R", "a") as file:
    file.write("chooseCRANmirror(graphics=FALSE, ind=34)\n")
    file.write("try({\n")
    for package in packages:
        file.write("install.packages(\'" + package + "\', lib = \'/opt/R/new_library/R/library\')\n")
    file.write("})\n")

connection.upload_file("tmp.R", "/home/ec2-user/tmp.R")
out, out_err = connection.send_command("/opt/R/bin/Rscript --verbose /home/ec2-user/tmp.R")

if len(out) > 0:
    logger.info(concatenate_list_data(out_err))
else:
    logger.error(concatenate_list_data(out_err))

os.remove("tmp.R")

logger.info("Download packages")

connection.send_command("cd /opt/R/new_library && zip -r -q packages.zip R/")
connection.download_file("/opt/R/new_library/packages.zip", "packages.zip")

if arguments.terminate:
    instance.terminate_instance(my_server_id)
