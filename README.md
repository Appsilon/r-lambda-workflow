# r-lambda-workflow

## Building R

1. Start an EC2 instance using [Lambda AMI](https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#Images:visibility=public-images;search=amzn-ami-hvm-2017.03.1.20170812-x86_64-gp2;sort=name).
2. Copy `build_r.sh` to the instance.
3. Run `build_r.sh` with R version as a parameter (e.g. `3.5.1`).

## Configuring the AWS services

1. Upgrade aws cli: `pip install awscli --upgrade --user`
2. Configure credentials: `aws configure`
