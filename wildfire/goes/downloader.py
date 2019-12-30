# pylint: disable=line-too-long
"""S3 interface to download NASA/NOAA GOES-R satellite images.

This module uses the boto3 library to interact with Amazon S3. boto3 requires the user to
supply their access key id and secret access key. To provide boto3 with the necessary
credentials the user must either have a `~/.aws/credentials` file, or the environment
variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` set. See this package's README.md
or boto3's documentation at https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file for more information.
"""
import datetime
import logging
import os
import tempfile

import boto3
import xarray as xr

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


def persist_s3(s3_bucket, s3_key, local_directory):
    """Download and persist specific scan from S3.

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
        "Persisting s3://%s/%s to %s", s3_bucket, s3_key, local_filepath,
    )
    s3.download_file(Bucket=s3_bucket, Key=s3_key, Filename=local_filepath)
    return local_filepath


def check_size_with_user(size):
    """Check size of download with the user.

    Parameters
    ----------
    size : float
        Download size in gigabytes.
    """
    prompt = f"About to download {size:.0f}GB of data. Continue? [y/n]: "
    prompt_accepted = False

    while not prompt_accepted:
        answer = input(prompt).lower().strip()
        if answer == "y":
            prompt_accepted = True
        elif answer == "n":
            raise AssertionError(f"User does not want to download {size:.0f}GB of data")


def read_s3(s3_bucket, s3_key):
    """Read specific scan from S3 as xarray Dataset.

    Parameters
    ----------
    s3_bucket : str
    s3_key : str

    Returns
    -------
    xr.core.dataset.Dataset
    """
    s3 = boto3.client("s3")
    with tempfile.NamedTemporaryFile() as temp_file:
        s3.download_file(Bucket=s3_bucket, Key=s3_key, Filename=temp_file.name)
        dataset = xr.open_dataset(temp_file.name)
    return dataset


def download_batch(s3_object_summaries, local_directory):
    """Download batch of satellite scans from Amazon S3 matching input.

    Parameters
    ----------
    s3_object_summaries : list of boto3.ObjectSummary
        The output of `downloader.query_s3()` can be used as input here.
    local_directory : str
        Path to local directory at which to persist scans.

    Returns
    -------
    list[str]
        List of downloaded filepaths.
    """
    _logger.info(
        "Downloading %dGB of data...",
        int(sum(map(lambda scan: scan.size, s3_object_summaries)) / 1e9),
    )
    filepaths = []
    for s3_scan in s3_object_summaries:
        filepaths.append(
            persist_s3(
                s3_bucket=s3_scan.bucket_name,
                s3_key=s3_scan.key,
                local_directory=local_directory,
            )
        )
    return filepaths


def _is_good_object(key, regions, channels, start, end):
    """Check if object should be downloaded, given parameters.

    Check that the object is in the desired regions, channels, and date range.

    Parameters
    ----------
    key : str
        S3 key.
    regions : list[str]
    channels : list[int]
    start : datetime.datetime
        Start of date range.
    end : datetime.datetime
        End of date range.

    Returns
    -------
    Boolean
    """
    region, channel, _, scan_started_at = utilities.parse_filename(filepath=key)
    return (
        (region in regions)
        and (channel in channels)
        and (start <= scan_started_at <= end)
    )


def query_s3(satellite, regions, channels, start, end):
    """Query Amazon S3 for data files that match the input.

    Parameters
    ----------
    satellite : str
        Amazon S3 bucket name. Either noaa-goes16 or noaa-goes17
    regions : list[str]
        "F", "C", "M1", or "M2"
    channels : list[int]
        1 - 16
    start : datetime.datetime
    end : datetime.datetime

    Returns
    -------
    list[boto3.resources.factory.s3.ObjectSummary]
    """
    _logger.info(
        """Querying for s3 objects with the following properties:
    satellite: %s
    regions: %s
    channels: %s
    start date: %s
    end date: %s""",
        satellite,
        regions,
        channels,
        start,
        end,
    )
    s3 = boto3.resource("s3")
    key_path_format = "{product_description}/{year}/{day_of_year}/{hour}/"
    product_description_format = "ABI-L1b-Rad{region}"

    scans = []
    for region in regions:
        # only use the first character from region (M1 or M2 -> M)
        product_description = product_description_format.format(region=region[0])

        current = start.replace(minute=0, second=0, microsecond=0)
        while current <= end:
            key_filter = key_path_format.format(
                product_description=product_description,
                year=current.year,
                day_of_year=current.strftime("%j"),
                hour=current.strftime("%H"),
            )
            s3_scans = [
                s3_object
                for s3_object in s3.Bucket(satellite).objects.filter(Prefix=key_filter)
                if _is_good_object(
                    key=s3_object.key,
                    regions=regions,
                    channels=channels,
                    start=start,
                    end=end,
                )
            ]
            scans += s3_scans
            current += datetime.timedelta(hours=1)
    return scans
