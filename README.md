# Wildfire

![Status Badge](https://github.com/joyprojects/wildfire/workflows/CI/badge.svg)

This is a repository for the purpose of predicting characteristics about wildfires from
geostationary satellite imagery.

## Contents

- [Installation](#Installation)
  - [Instructions](#Instructions)
  - [Requirements](#Requirements)
- [bin/](#bin/)
- [documentation/](#documentation/)
- [wildfire/goes/](#wildfire/goes/)
- [wildfire/threshold_model/](#wildfire/threshold_model/)
- [wildfire/wildfire.py](#wildfire/wildfire.py)
- [NAS](#NAS)

## Installation

The developers both suggest and use [conda](https://www.anaconda.com/distribution/) for
managing python environments.

Before starting the installation process, we strongly suggest setting up this package in
an isolated python environment. Below are several usefule commands for doing so with conda.

- `conda create --name wildfire3.7 python=3.7` to create a python environment for this project
- `source activate wildfire3.7` to activate the python environment
- `source deactivate` to deactivate the python environment
- `conda remove --name wildfire3.7 --all` to destroy the python environment (must deactivate first)

### Instructions

1. `cp .sample_env .env` and fill out any `<>` blocks
1. `set -o allexport && source .env && set +o allexport` to export environment variables
1. `pip install -r requirements.txt` to install dependencies
1. `conda install mpi4py torch cudatoolkit`
1. `pip install -r requirements-dev.in` to install test dependencies
1. `conda install pytorch cudnn` to install deep learning dependencies (add to requirements file?)
1. `scripts/test-it` to verify installation

### Requirements

1. To interact with S3 via [s3fs](https://s3fs.readthedocs.io/en/latest/)
one either needs to have credentials stored at `~/.aws/credentials` (see
[here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file))
or the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` set.

## bin/

There are currently two main entry scripts for this package, `bin/download_satellite_data`
`bin/label_wildfires` which are meant to bulk download GOES satellite data, and label GOES
satellite data with wildfires.

`bin/download_satellite_data noaa-goes17 M1 2019-01-01T01:00:00 2019-02-01T01:11:00 downloaded_data`

- To download GOES data from the GOES-17 satellite over the mesoscale 1 region between Jan 1, 2019 01:00 AM and Feb 1, 2019 01:11 AM to the "downloaded_data/" directory

`bin/label_wildfires noaa-goes17 M1 2019-01-01T01:00:00 2019-02-01T01:00:00 goes_data labeled_wildfires`

- To label wildfires in GOES data from the GOES-17 satellite over the mesoscale 1 region between Jan 1, 2019 01:00 AM and Feb 1, 2019 01:00 AM found in the "goes_data/" directory and persist any wildfires found to the "labeled_wildfires" directory

- (MPI) Fires can be labeled in parallel across multiple nodes on NAS. mpi4py is used to distribute scans across the number of nodes,`bin/label_wildfires.mpi.py`. This script is executed across several nodes and processed with a PBS job, `bin/label_wildfires.mpi.pbs`. Please review and edit selected queues, number of nodes/cpus, and mpi process size in `*.pbs` scripts. For job setup see [https://www.nas.nasa.gov/hecc/support/kb/121/]

## documentation/

Various documentation around GOES satellite data, modelling, package usage, and working on
NAS.

## wildfire/goes/

Utilities for using NOAA's GOES-16/17 satellite data, which is publicly accessible in
 Amazon S3. See `documentation/notesbooks/example_usage.ipynb` for examples.

## wildfire/threshold_model/

Implementation of Xu Zhong's threshold model for detecting wildfires (see
[this paper](https://www.researchgate.net/publication/318455389_Real-time_wildfire_detection_and_tracking_in_Australia_using_geostationary_satellite_Himawari-8)
for more information). See `documentation/notesbooks/example_usage.ipynb` for examples of
our implementation, and
`documentation/notesbooks/wildfire_detection_threshold_model.ipynb` for going through
their paper.

## wildfire/wildfire.py

Utilities for combining GOES satellite data and the wildfire detection threshold model to
produce detection predictions. See `documentation/notesbooks/example_usage.ipynb` for
examples.

## NAS

We developed this package with working in the NAS super-compute environment heavily in
mind. Thus, we have worked a lot in it, and wanted to persist some of our learnings here
for others to use (see `documentation/nas/`). We do want to make clear, however, that our
notes are not meant as a replacement for the official documentation, merely a supplement.
If you are setting up your NAS environment for the first time please refer to
[their documentation](https://www.nas.nasa.gov/hecc/support/kb/), or if you are looking
 for support please contact them for 24/7 service at 800-331-8737 or
 <support@nas.nasa.gov>.
