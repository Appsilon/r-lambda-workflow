# AWS Lambda runtime for R

This repository provides runtime for running `R` on AWS Lambda. It also provides a workflow for using dependecies like R packages by creating additional layers.

AWS Lambda is a serverless solution for running scripts triggered by various events. It supports several runtimes by default (including `Python`, `Go`, `Java`, `C#`, `Node.js`, `Ruby` and `PowerShell`), but it is possible to create custom runtime environments to use almost any other, non-supported language.

This approach uses AWS Lambda component, namely _layers_, as containers for `R` environment and provided packages. In your lambda function, you can use pre-built layers we provide or you can create your own ones with specific content (different `R` version, custom packages, etc.).

## Using R in AWS Lambda

Using R scripts in AWS Lambda is just a few steps:

1. In [AWS Console](https://console.aws.amazon.com/lambda) create a new function (suggested region: `eu-central-1`). Choose `Custom runtime`.
2. After creating new function:
    1. In _Function code_ create a new script with `.R` extension, for example `my_script.R`.
    2. Paste function code inside, for example `hello_world <- function() { "Hello world!" }`
    3. Change `Handler`  to `[script file name].[function name]`.
    4. Delete `bootstrap` and `hello.sh` files created by AWS. We don't need them, because the R runtime provides its own version of `bootstrap`.
    5. In _Basic settings_, change `Timeout`  to 30 seconds or more. Since `R` is not a speed demon, the default value (3 seconds) is too low.
3. Add R layer:
    1. In _Designer_ panel click _Layers_ to open layers configuration for your Lambda. This is where we need to add layer containing the `R` runtime.
    2. Go to `Currently available layers` below and choose the base layer in your region. Add a layer giving its ARN. For example, for `eu-central-1`, the ARN is `arn:aws:lambda:eu-central-1:599651763768:layer:basic-r:1`.
    3. If your code needs any additonal packages, they should be added additional layers. Go to **Creating custom layers** below to learn how to create such layers. After you create a layers, simply add it by providing layer ARN.  You can provide up to 5 layers. Lambda will look for required dependencies (e.g. packages) in them, in provided order. **Always use R layer as the first one.** Packages should be included as additional layers.
4. That's it! Now you can save and test your function. Remember to provide proper input data in JSON format - in our example it should be empty.

### Pre-built layers

In your Lambda you can use published pre-built layers.

##### Currently available layers:

| layer arn                                                | region       | content                               |
| -------------------------------------------------------- | ------------ | ------------------------------------- |
| arn:aws:lambda:eu-central-1:599651763768:layer:basic-r:1 | eu-central-1 | R 3.5.1                               |
| arn:aws:lambda:eu-central-1:599651763768:layer:dplyr     | eu-central-1 | dplyr (with dependencies) for R 3.5.1 |

**A layer can be used only in the provided region!** If there's no layer for your region, you can create one (for how to do that see _Basic R layer_ below) or open an issue in this repo asking for one.

## Creating custom R layers

If you need packages that are not provided in the prebuilt layers, you neet to create additional layers containing them. See [R packages Layer](#r-packages-layer) for instructions how to do that. You'll create an instance, install packages and extract them into a Lambda layer. We provide an AMI and scripts that make this straightforward.

If you need a different version of R than provided, you'll need to create a basic `R` layer, follow the instruction provided in [Basic R Layer](#basic-r-layer) section. Creating AMI (to use it later for `R` packages layers) is described in [Lambda AMI with R](#lambda-ami-with-r) section.

#### Configuring the AWS services

To be able to use this workflow, you have to configure AWS services.

1. Install/upgrade aws cli: `pip install awscli --upgrade --user`
2. Configure credentials: `aws configure` (provide: AWS Access Key ID, AWS Secret Access Key, Default region name)
3. You need a Key Pair to be able to connect to EC2 instances. If you do not have one, you can create it in the Amazon EC2 console or using `aws cli`: `aws ec2 create-key-pair --key-name [key name] --query 'KeyMaterial' --output text >> [file name].pem` (**Important:** Key file name has to be the same as the key name!). You will have to provide the path to the private key as a script argument (`-k` flag) in the next steps.

Note: the instance will use your default security group. Make sure that it is open for incoming traffic from your IP on port 22 so that the script can connect and install needed packages on the instance.

#### Other requirements

Required `Python` libraries are described in `Pipfile`. It is recommended to use this workflow with virtual environment, which can be set up with [`pipenv` library](https://pipenv.kennethreitz.org/).

### Basic R Layer

1. Run `./setup_r_instance.py -k [path to private key]`. It will create an EC2 instance, install R and download the archive `R.zip`. Check `./setup_r_instance.py --help` for options. You have to provide at least the path to the private key (`-k`). Script by default terminates the instance. If you want to prevent it set `-t=False`.
2. Run `./build_runtime.sh` script. It will create an archive `runtime.zip` with R runtime for AWS Lambda.
3. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://runtime.zip`

### Lambda AMI with R

1. Run `./setup_r_instance.py  -k [path to private key] -a create_ami -n [new ami name]`. It will create EC2 instance, install R and create AMI. Check `./setup_r_instance.py --help` for options. You have to provide at least three parameters: `-k` path to the private key (e.g. `~/.ssh/key.pem`); `-a create_ami` action; `-n` AMI name. Script by deafult terminates the instance. If you want to prevent it set `-t=False`. Script will create AMI.

### R packages Layer

1. Run `./r_package_layer.py  -k [path to private key] -m [R Lambda AMI id] -p [packages to install]`. It will create an instance from AMI with R preinstalled, install required packages and download archive `packages.zip`. Check `./r_package_layer.py --help` for options. You have to provide at least three parameters: `-k` path to the private key (e.g. `~/.ssh/key.pem`); `-m` Lambda AMI with preinstalled R id; `-p` packages to install (if more than one, pass in quotes e.g. `"glue, stringr"`). Script by default terminates the instance. If you want to prevent it set `-t=False`.
2. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://packages.zip`

#### Pre-built AMI

| AMI name        | AMI id                | region       | conent  |
| --------------- | --------------------- | ------------ | ------- |
| r-lambda-ami_id | ami-0a1147e8e86aa6175 | eu-central-1 | R 3.5.1 |
|                 |                       |              |         |
