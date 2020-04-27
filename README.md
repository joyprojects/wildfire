# Wildfire

![Status Badge](https://github.com/joyprojects/wildfire/workflows/CI/badge.svg)

Use geostationary satellite imagery to forecast wildfires.

This library was born from researchers at NASA as a research tool. As such, the code
has been designed primarily for NASA's HPC environment, but also works for local
development. Namely, we use `dask` to distirbute computation across compute nodes and to
`dask-jobqueue` to interact with the PBS ecosystem.

Wildfire modelling, high performance computing (HPC), and working with satellite data all
have their quirks and so we have attempted to provide ample documentation in the form of
docstrings, readmes, and notebooks, in order to share our hard-fought learnings and ease
others' entry into these solving problems.

Although we do try to take advantage of various hardware and set ups that we can in order
to speed up computation, no specific hardware is required for using this library.

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

This repository requires [conda](https://www.anaconda.com/distribution/) for
managing its python environment and installing tricky packages. We have found that conda
offers significantly greater ease for installing packages like `pytorch` and `cudatoolkit`
which are used for modelling and GPU computation.

To ease the installation process we have created an install script which can be found in
`scripts/install`. More installation instructions are found below.

### Requirements

1. [Anaconda](https://docs.anaconda.com/anaconda/install/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
    1. some packages like `pytorch`, and `cudatoolkit` are much much much more easily installed using conda.

1. Amazon S3 credentials
    1. We use [s3fs](https://s3fs.readthedocs.io/en/latest/) to interact with Amazon S3,
    which requires one to have credentials stored at `~/.aws/credentials` (see
    [here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file)
    for how to create this file) or as environment variables `AWS_ACCESS_KEY_ID` and
    `AWS_SECRET_ACCESS_KEY`.

### Instructions

1. Make sure that all requirements above are set up or installed
1. `cp .sample_env .env` and fill out any `<>` blocks
1. `set -o allexport && source .env && set +o allexport` to export environment variables
1. `scripts/install` to create a virtual environement and set up the package for development.
1. `scripts/test-it` to verify install

## Entry Points

See the [wildfire/cli/](#wildfire/cli/) section below.

## Repository Structure

### dask_config/

This repository uses `dask` to distribute computation across available hardware. In local
development this takes advantage of computers having multiple cores (CPUs), and in HPC
environments having multiple compute nodes. Methods for using `dask` can be found in
`wildfire/multiprocess.py` in addition to examples in `examples/library_usage.ipynb`.

### documentation/

Various documentation and notebooks around GOES satellite data, modeling, package usage,
and high performance computing.

### wildfire/cli/

The command line interface (CLI) for the library. Currently, this handles downloading
satellite data, training wildfire models, and running inference. These jobs take advantage
of distributed or parallel processing when available.

More documentation is available throught the CLI:

- `download --help`
- `predict --help`
- `training-data --help`

### wildfire/data/

Modules for interacting with data used for wildfire modelling. All data used in this
library is publically accessible.

Currently, this includes uses the GOES-R Level 1 and Level 2 prodcuts with plans on
incoporating MODIS later.

The Geostationary Operational Environmental Satellites (GOES), operated by NOAA, provide
visibile and infrared imagery of the Earth, lightning mapping, space weather monitoring,
and solar imaging. Specifically, the GOES-16 and GOES-17 satellites are used broadly for
weather imaging and to this aim NOAA releases data from these two satellites publicly on
Amazon S3 (see
[here](https://s3.console.aws.amazon.com/s3/buckets/noaa-goes16/?region=us-east-1&tab=overview)
for GOES-16 data and
[here](https://s3.console.aws.amazon.com/s3/buckets/noaa-goes17/?region=us-east-1&tab=overview)
for GOES_17).

Data used in this library is explored in a lot more detail at `examples/goes_data.ipynb`.

#### /goes_level_1/

Geostationary satellite data closer to its "raw" form. This product includes spectral
radiance captures across 16 bands of light.

#### /goes_level_2/

More process satellite data that is specialized towards various weather and solar monitoring.
Specifically we use the wildfire fire product.

### wildfire/models/

Various models used to detect wildfires from geostationary satellite imagery.

#### /threshold_model/

Implementation of Xu Zhong et al's threshold model for detecting wildfires (see
their paper [here](https://www.researchgate.net/publication/318455389_Real-time_wildfire_detection_and_tracking_in_Australia_using_geostationary_satellite_Himawari-8)
for more information). See `examples/zhong_threshold_model.ipynb` for a
walkthrough of their paper, and `examples/library_usage.ipynb` for examples of our
implementation.

#### /dnn/

Various convolutional neural nets attempting to increase wildfire detection performance.

### wildfire/multiprocessing.py

Utilities for using `dask` for parallel and distributed processing. See
`examples/library_usage.ipynb` for examples.

## High Performance Computing (HPC)

We developed this package while working in the NAS super-compute environment. We found it
to be pretty tricky and nuanced and so we wanted to persist some of our learnings here
for others to use (see `documentation/nas/`). We do want to make clear, however, that our
notes are not meant as a replacement for the official documentation, merely a supplement.
If you are setting up your NAS environment for the first time please refer to
[their documentation](https://www.nas.nasa.gov/hecc/support/kb/), or if you are looking
for support please contact them for 24/7 service at 800-331-8737 or <support@nas.nasa.gov>.

Multiprocessing in this library was designed to work in both HPC environments and local
developement.

## TODO

- Run training data on NAS
- Maybe a multiprocessing explanation notebook for mpi4py, dask, multiprocessing, and ray
- Link to dask in README
- Update library usage notebook
- Update goes data notebook to instead just be data
- Add in DNN
- Run DNN training on NAS
- Make pylint and pydocstyle happy
- Run DNN inference on NAS
