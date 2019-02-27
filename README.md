# r-lambda-workflow

## Configuring the AWS services
_Important! awc cli should use Python 2!_

1. Upgrade aws cli: `pip install awscli --upgrade --user`
2. Configure credentials: `aws configure`
3. Create a key to connect to the aws instances.

## Basic R Layer

1. Create EC2 instance, install R and download the installation using `setup_r_instance.sh` script. Provide three parameters: (1) R version (e.g. `3.5.1`); (2) path to the key (e.g. `~/.ssh/key.pem`); (3) `buildr` (to build and download R). Script will download archive with R (`R-{R version}.zip`).
2. Create runtime using `build_runtime.sh` script with R version as a parameter (e.g. `3.5.1`).
3. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://runtime.zip`

## Lambda AMI with R

1. Create EC2 instance, install R and create AMI using `setup_r_instance.sh` script. Provide three parameters: (1) R version (e.g. `3.5.1`); (2) path to the key (e.g. `~/.ssh/key.pem`); (3) `ami`. Script will create AMI.

## R packages Layer

1. Create instance from AMI with R preinstalled, install required packages and download zip using `r_package_layer.sh`. You have to provide three parameters: (1) path to the key (e.g. `~/.ssh/key.pem`); (2) id of the image with preinstalled R; (3) name of the R package to be installed. Script will download the archive `packages.zip`.
2. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://packages.zip`
