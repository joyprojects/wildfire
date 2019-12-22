"""S3 interface to download NASA/NOAA GOES-R satellite images."""
import datetime
import logging
import math
import os

import boto3
from tqdm import tqdm

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


def download_batch(satellite, regions, channels, start, end, local_directory):
    """Download batch of satellite scans from Amazon S3 matching input.

    Parameters
    ----------
    satellite : str
    regions : list(str)
    channels : list(int)
    start : datetime.datetime
    end : datetime.datetime
    local_directory : str
        Path to local directory at which to persist scans.

    Returns
    -------
    list[str]
        List of downloaded filepaths.
    """
    s3_scans = query_s3(
        satellite=satellite, regions=regions, channels=channels, start=start, end=end
    )
    filepaths = []
    for s3_scan in s3_scans:
        filepaths.append(
            download_scan(
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
    region, channel, _, scan_started_at = utilities.parse_filepath(filepath=key)
    return (
        (region in regions)
        and (channel in channels)
        and (start <= scan_started_at <= end)
    )


def _num_hours_to_check(start, end):
    """Calculate the number of hours of scand to retrieve from Amazon S3.

    Parameters
    ----------
    start : datetime.datetime
        Start of date range.
    end : datetime.datetime
        End of date range.

    Returns
    -------
    int
        The number of hours to retrieve from Amazon S3 rounded up to nearest hour. This is
        primarily used as a range for tqdm's progressbar.
    """
    return math.ceil((end - start).total_seconds() / 3600)


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
    for region in tqdm(regions, desc="Regions"):
        # only use the first character from region (M1 or M2 -> M)
        product_description = product_description_format.format(region=region[0])

        current = start.replace(minute=0, second=0, microsecond=0)
        inner_progress_bar = tqdm(total=_num_hours_to_check(start=current, end=end), desc="Hours")
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
            inner_progress_bar.update(1)
        inner_progress_bar.close()
    return scans
