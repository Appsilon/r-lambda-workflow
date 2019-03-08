# r-lambda-workflow

This workflow allows you to create a custom runtime environment for AWS Lambda where scripts written in R can be deployed.

To deploy an R function as Lambda, you need:
1. Layer with R:
  * use a layer previously prepared (see [Existing layers and AMI](#existing-layers-and-ami))
  * create new layer with basic R (see [Basic R Layer](#basic-r-layer))
2. Layer with additional packages (if required):
  * use a layer previously prepared (see [Existing layers and AMI](#existing-layers-and-ami))
  * create new layer with required packages (see [R packages Layer](#r-packages-layer)). Creating layer with R packages requires AMI with R preinstalled. You can use one previously prepared (see [Existing layers and AMI](#existing-layers-and-ami)) or create a new one (see [Lambda AMI with R](#lambda-ami-with-r)).

Provide those layers to your function. Layer with basic R has to be merged as first.

### Configuring the AWS services

To be able to use this workflow, you have to configure AWS serives.

1. Install/upgrade aws cli: `pip install awscli --upgrade --user`
2. Configure credentials: `aws configure` (provide: AWS Access Key ID, AWS Secret Access Key, Default region name)
3. You need a Key Pair to be able to connect to EC2 instances. If you do not have one, you can create it in the Amazon EC2 console or using `aws cli`: `aws ec2 create-key-pair --key-name [key name] --query 'KeyMaterial' --output text >> [file name].pem` (**Important:** Key file name has to be the same as key name!). You will have to provide the path to the private key as a script argument (`-k` flag) in the next steps.

Note: the instance will use your default security group. Make sure that it is open for incoming traffic from your IP on port 22, so that the script can connect and install needed packages on the instance.

## Basic R Layer

1. Run `./setup_r_instance.py -k [path to private key]`. It will create EC2 instance, install R and download the archive `R.zip`. Check `./setup_r_instance.py --help` for options. You have to provide at least the path to the private key (`-k`). Script by deafult terminates the instance. If you want to prevent it set `-t=False`.
2. Run `./build_runtime.sh` script. It will create an archive `runtime.zip` with R runtime for AWS Lambda.
3. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://runtime.zip`

## Lambda AMI with R

1. Run `./setup_r_instance.py  -k [path to private key] -a create_ami -n [new ami name]`. It will create EC2 instance, install R and create AMI. Check `./setup_r_instance.py --help` for options. You have to provide at least three parameters: `-k` path to the private key (e.g. `~/.ssh/key.pem`); `-a create_ami` action; `-n` AMI name. Script by deafult terminates the instance. If you want to prevent it set `-t=False`. Script will create AMI.

## R packages Layer

1. Run `./r_package_layer.py  -k [path to private key] -m [R Lambda AMI id] -p [packages to install]`. It will create instance from AMI with R preinstalled, install required packages and download archive `packages.zip`. Check `./r_package_layer.py --help` for options. You have to provide at least three parameters: `-k` path to the private key (e.g. `~/.ssh/key.pem`); `-m` Lambda AMI with preinstalled R id; `-p` packages to install (if more than one, pass in quotes e.g. `"glue, stringr"`). Script by deafult terminates the instance. If you want to prevent it set `-t=False`.
2. Create a new layer: `aws lambda publish-layer-version --layer-name [layer name] --zip-file fileb://packages.zip`

## Using R Runtime - example

1. In [AWS Console](https://console.aws.amazon.com/lambda) create a new function. Choose `Custom runtime`.
2. After creating new function:
  * Remove `bootstrap` and `hello.sh` files. Create new script with `.R` extension (e.g. `my_script.R`). Paste sample function inside: `hello_world <- function() {return("Hello world!")}`
  * Change **Handler** to `[R script name (without extension)].[function name]` (as in example: `my_script.hello_world`)
  * Change **Timeout** to 60 seconds
3. Add R layer:
  * Go to [AWS Lambda](https://console.aws.amazon.com/lambda) > Layers
  * Copy the ARN of the R Layer
  * Go to your function and select **Layers**
  * Add layer using ARN
4. You can test your function (remember to provide proper input data in JSON format - in this example it should be empty).

## Existing layers and AMI

#### Currently existing Layers

| layer arn                                                | region       | content                               |
| -------------------------------------------------------- | ------------ | ------------------------------------- |
| arn:aws:lambda:eu-central-1:599651763768:layer:basic-r:1 | eu-central-1 | R 3.5.1                               |
| arn:aws:lambda:eu-central-1:599651763768:layer:dplyr     | eu-central-1 | dplyr (with dependencies) for R 3.5.1 | 

#### Currently existing AMI

| AMI name          | AMI id              | region       | conent  |
| --------------- | --------------------- | ------------ | ------- |
| r-lambda-ami_id | ami-0a1147e8e86aa6175 | eu-central-1 | R 3.5.1 |
