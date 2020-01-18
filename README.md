# Wildfire

![Status Badge](https://github.com/joyprojects/wildfire/workflows/CI/badge.svg)

This is a repository for the purpose of predicting characteristics about wildfires from
geostationary satellite imagery.

## Contents

- [Installation](#Installation)
  - [Instructions](#Instructions)
  - [Requirements](#Requirements)
- [documentation/](#documentation/)
- [wildfire/goes/](#wildfire/goes/)
- [wildfire/threshold_model/](#wildfire/threshold_model/)
- [wildfire/wildfire.py](#wildfire/wildfire.py)
- [NAS](#NAS)

## Installation

The developers both suggest and use [conda](https://www.anaconda.com/distribution/) for
managing python environments.

Before starting the installation process, we strongly suggest setting up this package in an isolated
python environment. Below are several usefule commands for doing so with conda.

- `conda create --name wildfire3.7 python=3.7` to create a python environment for this project
- `source activate wildfire3.7` to activate the python environment
- `source deactivate` to deactivate the python environment
- `conda remove --name wildfire3.7 --all` to destroy the python environment (must deactivate first)

### Instructions

1. `cp .sample_env .env` and fill out any `<>` blocks
1. `set -o allexport && source .env && set +o allexport` to export environment variables
1. `pip install -r requirements.txt` to install dependencies
1. `pip install -r requirements-dev.in` to install test dependencies
1. `scripts/test-it` to verify installation

### Requirements

1. To interact with S3 via [s3fs](https://s3fs.readthedocs.io/en/latest/)
one either needs to have credentials stored at `~/.aws/credentials` (see [here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file)) or the environment variables
`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` set.

## documentation/

Checkout the `documentation/examples/` directory for interacting with GOES data and NAS code examples.
<!-- what can you find here? -->

## wildfire/goes/

Utilties for using NOAA's GOES-16/17 satellite data, which is publicly accessible in Amazon S3.
<!-- what is in this module? -->
<!-- what is goes? -->

## wildfire/threshold_model/

<!-- what is this modeule for? -->

## wildfire/wildfire.py

<!-- what is this module for? -->

## NAS

<!-- stuff about how this package is made to work on NAS, but you should learn about it yourself... we have provided some things we've learned along the way -->
<!-- link to documentation/nas/nas.md -->