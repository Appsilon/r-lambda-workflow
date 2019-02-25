# r-lambda-workflow

## Configuring the AWS services

All steps should be done in the previously created instance.

_Important! awc cli should use Python 2!_

1. Upgrade aws cli: `pip install awscli --upgrade --user`
2. Configure credentials: `aws configure`
3. Create a key to connect with the aws instances. Substitute its name and location in the `setup_r_instance.sh` file.
4. Create a security group with port 22 enabled. Substitute its name in the `setup_r_instance.sh` file.

## Basic R Layer

1. Create EC2 instance, install R and download the installation using `setup_r_instance.sh` script.
2. Create runtime using `build_runtime.sh` script with R version as a parameter (currently only 3.5.1).
3. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://runtime.zip`

## R packages Layer

TODO
