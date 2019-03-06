# r-lambda-workflow

## Configuring the AWS services

1. Upgrade aws cli: `pip install awscli --upgrade --user`
2. Configure credentials: `aws configure` (provide: AWS Access Key ID, AWS Secret Access Key, Default region name)
3. You need a Key Pair to be able to connect to EC2 instances. If you do not have one, you can create it in the Amazon EC2 console or using `aws cli`: `aws ec2 create-key-pair --key-name [key name] >> [file name].pem`. You will have to provide the path to the private key as a script argument (`-k` flag) in the next steps.

## Basic R Layer

1. Run `./setup_r_instance.py -k [path to private key]`. It will create EC2 instance, install R and download the archive `R.zip`. Check `./setup_r_instance.py --help` for options. You have to provide at least the path to the private key (`-k`). Script by deafult terminates the instance. If you want to prevent it set `-t=False`.
2. Run `./build_runtime.sh` script. It will create an archive `runtime.zip` with R runtime for AWS Lambda.
3. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://runtime.zip`

_To resolve!_

It is possible, that creating new layer will not work. Try changing Python version used by `aws cli`: you can change shebang in `~/.local/bin/aws`.

## Lambda AMI with R

1. Run `./setup_r_instance.py  -k [path to private key] -a create_ami -n [new ami name]`. It will create EC2 instance, install R and create AMI. Check `./setup_r_instance.py --help` for options. You have to provide at least three parameters: `-k` path to the private key (e.g. `~/.ssh/key.pem`); `-a create_ami` action; `-n` AMI name. Script by deafult terminates the instance. If you want to prevent it set `-t=False`. Script will create AMI.

## R packages Layer

1. Run `./r_package_layer.py  -k [path to private key] -m [R Lambda AMI id] -p [packages to install]`. It will create instance from AMI with R preinstalled, install required packages and download archive `packages.zip`. Check `./r_package_layer.py --help` for options. You have to provide at least three parameters: `-k` path to the private key (e.g. `~/.ssh/key.pem`); `-m` Lambda AMI with preinstalled R id; `-p` packages to install (if more than one, pass in quotes e.g. `"glue, stringr"`). Script by deafult terminates the instance. If you want to prevent it set `-t=False`.
2. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://packages.zip`

## Using R Runtime - example

1. In [AWS Console](https://console.aws.amazon.com/lambda) create new function. Choose `Custom runtime`.
2. After creating new function:
  * Remove `bootstrap` and `hello.sh` files. Create new script with `.R` file extension. Paste sample function inside: `hello_world <- function() {print("Hello world!")}`
  * Change **Handler** to `hello_world.handler`
  * Change **Timeout** to 60 seconds
3. Add R layer:
  * Go to [AWS Lambda](https://console.aws.amazon.com/lambda) > Layers
  * Copy the ARN of the R Layer
  * Go to your function and select **Layers**
  * Add layer using ARN
4. You can test your function (remember to provide proper input data - in this example it should be empty).
