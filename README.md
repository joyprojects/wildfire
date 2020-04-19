# Wildfire

![Status Badge](https://github.com/joyprojects/wildfire/workflows/CI/badge.svg)

This is a repository for the purpose of predicting characteristics about wildfires from
geostationary satellite imagery.

## Contents

- [Installation](#Installation)
  - [Requirements](#Requirements)
  - [Instructions](#Instructions)
- [Entry Points](#Entry-Points/)
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

### Requirements

1. [Anaconda](https://docs.anaconda.com/anaconda/install/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
    1. some packages like `pytorch`, and `cudatoolkit` are much much much more easily installed using conda.

1. To interact with S3 via [s3fs](https://s3fs.readthedocs.io/en/latest/)
one either needs to have credentials stored at `~/.aws/credentials` (see
[here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file))
or the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` set.

### Instructions

1. Make sure that all requirements above are installed
1. `cp .sample_env .env` and fill out any `<>` blocks
1. `set -o allexport && source .env && set +o allexport` to export environment variables
1. `scripts/install` to install package and dependencies
1. `scripts/test-it` to verify install

## Entry Points

- `download goes-level-1 2019-01-01 2019-01-02`
- `label goes-threshold 2019-01-01 2019-01-02`
- `training-data goes-l2-cnn /level_1_directory ./level_2_directory`

## documentation/

Various documentation around GOES satellite data, modelling, package usage, and working on
NAS.

## wildfire/cli/

The command line interface for the library. Currently, this handles downloading and labeling wildfires
in the GOES satellite data.

- `download --help`
- `predict --help`
- `training-data --help`

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

## TODO

- Run training data on NAS
- Add in DNN
- Run DNN training on NAS
- Make pylint and pydocstyle happy
- Run DNN inference on NAS
- Update all documentation
