import os
import time


def check_server_status(instance_id):
    command = f"aws ec2 describe-instance-status --instance-id {instance_id} --query 'InstanceStatuses[0].SystemStatus.Status' --output text --output text"
    return os.popen(command).read().strip()


def setup_instance(ami_id, instance_type, key_name):
    instance_id = os.popen(
        f"aws ec2 run-instances --image-id {ami_id} --count 1 --instance-type {instance_type} --key-name {key_name} --query 'Instances[0].InstanceId' --output text"
    ).read().strip()

    my_server_status = check_server_status(instance_id)

    while my_server_status != "ok":
        print("Waiting for instance")
        time.sleep(10)
        my_server_status = check_server_status(instance_id)

    instance_ip = os.popen(
        f"aws ec2 describe-instances --instance-id {instance_id} --query 'Reservations[0].Instances[0].PublicIpAddress' --output text"
    ).read().strip()

    return instance_ip, instance_id

def terminate_instance(instance_id):
    os.system(
        f"aws ec2 terminate-instances --instance-ids {instance_id}"
    )
