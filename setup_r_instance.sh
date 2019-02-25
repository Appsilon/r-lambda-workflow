#!/bin/bash
set -x

# create instance

MyServerID=$(aws ec2 run-instances --image-id ami-4fffc834 --count 1 --instance-type t2.micro --key-name kuba-appsilon --security-groups lambda-instance-group --query 'Instances[0].InstanceId' --output text)

MyServerCheckStatus=$(aws ec2 describe-instance-status --instance-id $MyServerID --query 'InstanceStatuses[0].SystemStatus.Status' --output text --output text)
while [ $MyServerCheckStatus != 'ok' ]; do
  sleep 10
  MyServerCheckStatus=$(aws ec2 describe-instance-status --instance-id $MyServerID --query 'InstanceStatuses[0].SystemStatus.Status' --output text --output text)
done

MyServerIP=$(aws ec2 describe-instances --instance-id $MyServerID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

# install R

ssh-keyscan -T 240 -H $MyServerIP &>> ~/.ssh/known_hosts
scp -i ~/.ssh/kuba-appsilon.pem build_r.sh ec2-user@$MyServerIP:/home/ec2-user/
ssh -i ~/.ssh/kuba-appsilon.pem ec2-user@$MyServerIP "chmod +x build_r.sh"
ssh -i ~/.ssh/kuba-appsilon.pem ec2-user@$MyServerIP "./build_r.sh 3.5.1"

# download R archive

scp -i ~/.ssh/kuba-appsilon.pem ec2-user@$MyServerIP:/opt/R/R-3.5.1.zip .
