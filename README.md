# GOES

This is a repository for working with GOES 16/17 satellite data. Core functionality includes
downloading, munging, and plotting.

## Contents

- [Installation](#Installation)
  - [Instructions](#Instructions)
- [Downloader](#Downloader)

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

## Downloader
