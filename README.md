# r-lambda-workflow

AWS Lambda is a serverless solution for running scripts triggered by various events. It supports several runtimes by defalut (including `Python`, `Go`, `Java`, `C#`, `Node.js`, `Ruby` and `PowerShell`), but it is possible to create custom runtime environments to use almost any other, non-suppored language. This repository provides access to the pre-build components of such runtime for `R`, together with a workflow for creating additional ones e.g. with specific R packages.

This approach uses AWS Lambda component, namely `layers`, as a containers for `R` environment and provided packages. In your lambda function, you can use already prepared layers or you can prepare ones with specific content (`R` version, custom packages etc.).

## Using R in AWS Lambda

Using R scripts in AWS Lambda with provided `layers` is quite simple. When creating new function, choose `Custom runtime`. Create your function in `*.R` script and provide script and function name in `Handler` field (`[script name].[function name]`).
Base `R` and packages should be added as a layers. It can be done simply by providing layer ARN.  You can provide up to 5 layers. Lambda will look for required dependencies (e.g. packages) in them, in provided order. **Always use R layer as the first one.** Packages should be included as additional layers.

Note: Since `R` is not a speed demon, you should icrease function timeout. Default value (3 seconds) is too low.

### Pre-build layers

In your Lambda you can use published pre-build layers.

##### Currently available layers:

| layer arn                                                | region       | content                               |
| -------------------------------------------------------- | ------------ | ------------------------------------- |
| arn:aws:lambda:eu-central-1:599651763768:layer:basic-r:1 | eu-central-1 | R 3.5.1                               |
| arn:aws:lambda:eu-central-1:599651763768:layer:dplyr     | eu-central-1 | dplyr (with dependencies) for R 3.5.1 |

##### Using R Runtime - example

1. In [AWS Console](https://console.aws.amazon.com/lambda) create a new function (region: `eu-central-1`). Choose `Custom runtime`.
2. After creating new function:
  * Remove `bootstrap` and `hello.sh` files. Create new script with `.R` extension (e.g. `my_script.R`). Paste sample function inside: `hello_world <- function() {return("Hello world!")}`
  * Change **Handler** to `[R script name (without extension)].[function name]` (as in example: `my_script.hello_world`)
  * Change **Timeout** to 60 seconds
3. Add R layer:
  * Go to your function and select **Layers**
  * Add layer using ARN: `arn:aws:lambda:eu-central-1:599651763768:layer:basic-r:1`
4. You can test your function (remember to provide proper input data in JSON format - in this example it should be empty).

## Creating custom R layers

If you want to use specific version of `R` or you have to use packages that are not provided in the prebuild layers, you will have to create layers on your own.
If you are using pre-build `R` layer and you have access to AMI with preinstalled `R`, you can create instance, install required packages and download them in a simple way using `r_package_layer.py` script. Detailed description is provided in [R packages Layer](#r-packages-layer) section.
If you want to create basic `R` layer, follow instruction provided in [Basic R Layer](#basic-r-layer) section.
Creating AMI (to use it later for `R` packages layers) is described in [Lambda AMI with R](#lambda-ami-with-r) section.

#### Configuring the AWS services

To be able to use this workflow, you have to configure AWS serives.

1. Install/upgrade aws cli: `pip install awscli --upgrade --user`
2. Configure credentials: `aws configure` (provide: AWS Access Key ID, AWS Secret Access Key, Default region name)
3. You need a Key Pair to be able to connect to EC2 instances. If you do not have one, you can create it in the Amazon EC2 console or using `aws cli`: `aws ec2 create-key-pair --key-name [key name] --query 'KeyMaterial' --output text >> [file name].pem` (**Important:** Key file name has to be the same as key name!). You will have to provide the path to the private key as a script argument (`-k` flag) in the next steps.

Note: the instance will use your default security group. Make sure that it is open for incoming traffic from your IP on port 22, so that the script can connect and install needed packages on the instance.

### Basic R Layer

1. Run `./setup_r_instance.py -k [path to private key]`. It will create EC2 instance, install R and download the archive `R.zip`. Check `./setup_r_instance.py --help` for options. You have to provide at least the path to the private key (`-k`). Script by deafult terminates the instance. If you want to prevent it set `-t=False`.
2. Run `./build_runtime.sh` script. It will create an archive `runtime.zip` with R runtime for AWS Lambda.
3. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://runtime.zip`

### Lambda AMI with R

1. Run `./setup_r_instance.py  -k [path to private key] -a create_ami -n [new ami name]`. It will create EC2 instance, install R and create AMI. Check `./setup_r_instance.py --help` for options. You have to provide at least three parameters: `-k` path to the private key (e.g. `~/.ssh/key.pem`); `-a create_ami` action; `-n` AMI name. Script by deafult terminates the instance. If you want to prevent it set `-t=False`. Script will create AMI.

### R packages Layer

1. Run `./r_package_layer.py  -k [path to private key] -m [R Lambda AMI id] -p [packages to install]`. It will create instance from AMI with R preinstalled, install required packages and download archive `packages.zip`. Check `./r_package_layer.py --help` for options. You have to provide at least three parameters: `-k` path to the private key (e.g. `~/.ssh/key.pem`); `-m` Lambda AMI with preinstalled R id; `-p` packages to install (if more than one, pass in quotes e.g. `"glue, stringr"`). Script by deafult terminates the instance. If you want to prevent it set `-t=False`.
2. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://packages.zip`

#### Pre-build AMI

| AMI name        | AMI id                | region       | conent  |
| --------------- | --------------------- | ------------ | ------- |
| r-lambda-ami_id | ami-0a1147e8e86aa6175 | eu-central-1 | R 3.5.1 |
|                 |                       |              |         |
