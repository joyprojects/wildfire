# Wildfire

![](https://github.com/joyprojects/wildfire/workflows/CI/badge.svg)

This is a repository for for the purpose of predicting characteristics about wildfires from
geostationary satellite imagery.

## Contents

- [Installation](#Installation)
  - [Instructions](#Instructions)
  - [Requirements](#Requirements)
- [goes/](#goes/)

## Installation

The developers both suggest and use [conda](https://www.anaconda.com/distribution/) for
managing python environments.

Before starting the installation instructions, we strongly suggest doing so in an isolated
python environment. Below are several usefule commands for doing so with conda.

- `conda create --name wildfire.6 python=3.6` to create a python environment for this project
- `source activate wildfire.6` to activate the python environment
- `source deactivate` to deactivate the python environment
- `conda remove --name wildfire.6 --all` to destroy the python environment (must deactivate first)

### Instructions

1. `cp .sample_env .env` and fill out any `<>` blocks
1. `set -o allexport && source .env && set +o allexport` to export environment variables
1. `pip install -r requirements.txt` to install dependencies
1. `scripts/test` to verify installation

### Requirements

1. To interact with S3 via [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
one either needs to have credentials stored at `~/.aws/credentials` (see [here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file)) or the environment variables
`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` set.

## Examples

Checkout the `examples/` directory for example notebooks.

## goes/

Utilties for using NOAA's GOES-16/17 satellite data, which is publicly accessible in Amazon S3.
