#!/bin/bash
set -x

VERSION=$1
KEY_PATH=$2
ACTION=$3

KEY_NAME=$(echo $KEY_PATH | rev | cut -d '/' -f 1 | cut -d '.' -f 2 | rev)

# create instance

MyServerID=$(aws ec2 run-instances --image-id ami-4fffc834 --count 1 --instance-type t2.micro --key-name $KEY_NAME --query 'Instances[0].InstanceId' --output text)

MyServerCheckStatus=$(aws ec2 describe-instance-status --instance-id $MyServerID --query 'InstanceStatuses[0].SystemStatus.Status' --output text --output text)
while [ $MyServerCheckStatus != 'ok' ]; do
  sleep 10
  MyServerCheckStatus=$(aws ec2 describe-instance-status --instance-id $MyServerID --query 'InstanceStatuses[0].SystemStatus.Status' --output text --output text)
done

MyServerIP=$(aws ec2 describe-instances --instance-id $MyServerID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

# install R

ssh-keyscan -T 240 -H $MyServerIP &>> ~/.ssh/known_hosts
scp -i $KEY_PATH build_r.sh ec2-user@$MyServerIP:/home/ec2-user/
ssh -i $KEY_PATH ec2-user@$MyServerIP "chmod +x build_r.sh"
ssh -i $KEY_PATH ec2-user@$MyServerIP "./build_r.sh $VERSION"

# download R archive
if [ $ACTION == "buildr" ]; then
  scp -i $KEY_PATH ec2-user@$MyServerIP:/opt/R/R-$VERSION.zip .
elif [ $ACTION == "ami" ]; then
  aws ec2 create-image --instance-id $MyServerID --name "r-ami" --description "Lambda AMI with R"
fi
