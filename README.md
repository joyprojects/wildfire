# GOES

This is a repository for working with GOES 16/17 satellite data. Core functionality includes
downloading, munging, and plotting.

## Contents

- [Installation](#Installation)
  - [Instructions](#Instructions)
  - [Requirements](#Requirements)
- [Downloader](#Downloader)

## Data

This repository uses the publicly-accessible NOAA GOES 16 data found at [s3](https://s3.console.aws.amazon.com/s3/buckets/noaa-goes16/ABI-L1b-RadM/?region=us-west-2), specifically the ABI-L1b-RadM product.

## Installation

The developers both suggest and use [conda](https://www.anaconda.com/distribution/) for
managing python environments.

Before starting the installation instructions, we strongly suggest doing so in an isolated
python environment. Below are several usefule commands for doing so with conda.

- `conda create --name goes3.6 python=3.6` to create a python environment for this project
- `source activate goes3.6` to activate the python environment
- `source deactivate` to deactivate the python environment
- `conda remove --name goes3.6 --all` to destroy the python environment (must deactivate first)

### Instructions

1. `cp .sample_env .env` and fill out any `<>` blocks
1. `set -o allexport && source .env && set +o allexport` to export environment variables
1. `pip install -r requirements.txt` to install dependencies
1. `scripts/test` to verify installation

### Requirements

1. To interact with S3 via [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
one either needs to have credentials stored at `~/.aws/credentials` (see [here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file)) or the environment variables
`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` set.

## Downloader
