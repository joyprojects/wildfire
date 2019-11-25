# Wildfire

![](https://github.com/joyprojects/wildfire/workflows/CI/badge.svg)

This is a repository for for the purpose of predicting characteristics about wildfires from
geostationary satellite imagery.

## Contents

- [Installation](#Installation)
  - [Instructions](#Instructions)
  - [Requirements](#Requirements)
- [goes/](#goes/)
- [NAS](#NAS)

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

## NAS

This project is meant to be deployed both locally and on NASA's NEX Super Computers.
1. For detailed documentation on a number of topics and bugs at NAS please see [here.](https://www.nas.nasa.gov/hecc/support/kb/)
1. For an overview of NAS Compute Architecture see [here.] 
1. Support can be reached easily by phone at 800-331-8737 and <support@nas.nasa.gov>.

### Conda on NAS

1. Conda is natively supported on NAS. On a given instance, to ensure that conda is loaded, please call:
`% module use -a /u/analytix/tools/modulefiles` and `% module load miniconda3/v4`.
1. You can create your own conda environments easily, and call them on any interactive or reserved node.

### Interactive Sessions

All users of NAS can launch an interactive PBS session with qsub, with a sample command found here:
`qsub -I -q v100 -l select=1:ncpus=1:model=sky_gpu,walltime=12:00:00`. The node ID (for instance `r101i0n4`) is constant 
per user (it does not change per different interactive sessions).

Alternatively, users can launch jobs via a PBS script. For more information please see [here](https://www.nas.nasa.gov/hecc/support/kb/using-conda-environments-for-machine-learning_557.html.
A sample script can be found in the examples folder as well.

### Reserved Notes

All users can reserve a compute nodes. For more information see [here.](https://www.nas.nasa.gov/hecc/support/kb/reserving-a-dedicated-compute-node_556.html)
These reserved nodes are nice ways to setup long-running Jupyter Notebooks. Users may have at most one reserved node.

To get information about the status of your reserved nodes, use: `pbs_rfe status`. 
To delete a reservation, use: `pbs_rfe delete R3286638` where `R3286638` is your reservation ID.

### SSH

When setting up your NAS environment, please setup:

1. [Public Key Authentication](https://www.nas.nasa.gov/hecc/support/kb/setting-up-public-key-authentication_230.html)  
for all pfes/sfes you intend to use (sfeX). Note that you do not need to this for all `lou` hosts, which is just storage.
1. [SSH Passthrough.](https://www.nas.nasa.gov/hecc/support/kb/setting-up-ssh-passthrough_232.html) 
This repository has an example `~/ssh/config`, including commonly needed ciphers.
1. When setting up an SSH Tunnel, please use: `ssh -L 5901:node_name:5901 pfe` where `node_name` is the name of the 
interactive or reserved node.
1. 

### Jupyter Notebooks on NAS.
1. Please walk through [Secure Jupyter Setup.](https://www.nas.nasa.gov/hecc/support/kb/secure-setup-for-using-jupyter-notebook-on-hecc-systems_576.html) 
Note that the instructions in the `Setting Up Jupyter` section are meant to be run on `sfe`, which contain the `/nasa` 
folder.
1. After, please navigate to [Using Jupyter for Machine Learning.](https://www.nas.nasa.gov/hecc/support/kb/using-jupyter-notebook-for-machine-learning_602.html)
1. It's easiest to deploy Jupyter from either a reserved or interactive node.
TODO: Figure how to to actually connect Jupyter Notebook.