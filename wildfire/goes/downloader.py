"""S3 interface to download NASA/NOAA GOES-R satellite images."""
import logging
import os

import boto3

from . import utilities

_logger = logging.getLogger(__name__)


def make_necessary_directories(filepath):
    """Create any directories in `filepath` that don't exist.

    Parameters
    ----------
    filepath : str
    """
    _logger.debug("Making necessary directories for %s", filepath)
    os.makedirs(name=os.path.dirname(filepath), exist_ok=True)


def download_scan(s3_bucket, s3_key, local_directory):
    """Download specific scan from S3.

    Parameters
    ----------
    s3_bucket : str
    s3_key : str
    local_directory : str

    Returns
    -------
    str
        File path scan was saved to.
    """
    s3 = boto3.client("s3")
    local_filepath = utilities.build_local_path(
        local_directory=local_directory, filepath=s3_key, satellite=s3_bucket
    )
    make_necessary_directories(filepath=local_filepath)
    _logger.info(
        "Downloading s3://%s/%s to %s", s3_bucket, s3_key, local_filepath,
    )
    s3.download_file(Bucket=s3_bucket, Key=s3_key, Filename=local_filepath)
    return local_filepath
