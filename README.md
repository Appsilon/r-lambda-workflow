# r-lambda-workflow

## Configuring the AWS services
_Important! awc cli should use Python 2!_

1. Upgrade aws cli: `pip install awscli --upgrade --user`
2. Configure credentials: `aws configure` (provide: AWS Access Key ID, AWS Secret Access Key, Default region name)
3. Create a pem key to connect to the aws instances.

### Basic R Layer

1. Create EC2 instance, install R and download the installation using `setup_r_instance.py` script. Check `./setup_r_instance.py --help` for options. You have to provide at least the path to the key (`-k`).
2. Create runtime using `build_runtime.sh` script with R version as a parameter (e.g. `3.5.1`, default in the previous script).
3. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://runtime.zip`

### Lambda AMI with R

1. Create EC2 instance, install R and create AMI using `setup_r_instance.py` script. Check `./setup_r_instance.py --help` for options. You have to provide at least three parameters: `-k` path to the key (e.g. `~/.ssh/key.pem`); `-a create_ami` action; `-n` AMI name. Script will create AMI.

### R packages Layer

1. Create instance from AMI with R preinstalled, install required packages and download zip using `r_package_layer.py`. Check `./r_package_layer.py --help` for options. You have to provide at least three parameters: `-k` path to the key (e.g. `~/.ssh/key.pem`); `-m` Lambda AMI with preinstalled R id; `-p` packages to install (if more than one, pass in quotes e.g. "glue, stringr"). Script will download the archive `packages.zip`.
2. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://packages.zip`
