# pylint: disable=line-too-long
"""S3 interface to interact with NASA/NOAA GOES-R satellite data.

This module uses the s3fs library to interact with Amazon S3. s3fs requires the user to
supply their access key id and secret access key. To provide boto3 with the necessary
credentials the user must either have a `~/.aws/credentials` file, or the environment
variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` set. See this package's README.md
or boto3's documentation at https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file for more information.
"""
import logging
import os

import s3fs

from . import utilities

SATELLITE_SHORT_HAND = {"noaa-goes16": "G16", "noaa-goes17": "G17"}
SATELLITE_UPPERCASE = {"noaa-goes16": "GOES16", "noaa-goes17": "GOES17"}

_logger = logging.getLogger(__name__)


def _decide_fastest_glob_patterns(satellite, region, start_time, end_time):
    base_pattern = f"{satellite}/ABI-L1b-Rad{region[0]}"

    def build(year, day_of_year, hour, filename):
        return "/".join([base_pattern, year, day_of_year, hour, filename,])

    if end_time is None:
        return [
            build(
                year=start_time.strftime("%Y"),
                day_of_year=start_time.strftime("%j"),
                hour=start_time.strftime("%H"),
                filename=f"OR_ABI-L1b-Rad{region}-M?C??_{SATELLITE_SHORT_HAND[satellite]}_s{start_time:%Y%j%H%M}*.nc",
            )
        ]

    if start_time.year != end_time.year:
        return [
            build(year=str(year), day_of_year="*", hour="*", filename="*.nc",)
            for year in range(start_time.year, end_time.year + 1)
        ]

    if start_time.date() != end_time.date():
        return [
            build(
                year=start_time.strftime("%Y"),
                day_of_year=str(day).zfill(3),
                hour="*",
                filename="*.nc",
            )
            for day in range(start_time.day, end_time.day + 1)
        ]

    if start_time.hour != end_time.hour:
        return [
            build(
                year=start_time.strftime("%Y"),
                day_of_year=start_time.strftime("%j"),
                hour=str(hour).zfill(2),
                filename="*.nc",
            )
            for hour in range(start_time.hour, end_time.hour + 1)
        ]

    return [
        build(
            year=start_time.strftime("%Y"),
            day_of_year=start_time.strftime("%j"),
            hour=start_time.strftime("%H"),
            filename="*.nc",
        )
    ]


def list_files(satellite, region, start_time, end_time=None):
    s3 = s3fs.S3FileSystem(anon=True, use_ssl=False)
    glob_patterns = _decide_fastest_glob_patterns(
        satellite=satellite, region=region, start_time=start_time, end_time=end_time
    )
    _logger.info("Listing files in S3 using glob patterns: %s", glob_patterns)
    return utilities.map_function(s3.glob, glob_patterns, flatten=True)


def download_file(s3_filepath, local_directory, s3):
    local_path = utilities.s3_filepath_to_local(
        s3_filepath=s3_filepath, local_directory=local_directory
    )
    os.makedirs(name=os.path.dirname(local_path), exist_ok=True)
    s3.get(rpath=s3_filepath, lpath=local_path)
    return local_path


def download_files(local_directory, satellite, region, start_time, end_time=None):
    s3 = s3fs.S3FileSystem(anon=True, use_ssl=False)

    s3_filepaths = list_files(
        satellite=satellite, region=region, start_time=start_time, end_time=end_time
    )

    _logger.info("Downloading %d files...", len(s3_filepaths))

    local_filepaths = utilities.starmap_function(
        function=download_file,
        function_args=[
            (s3_filepath, local_directory, s3) for s3_filepath in s3_filepaths
        ],
    )
    _logger.info(
        "Downloaded %d GB.", sum(os.path.getsize(f) for f in local_filepaths) / 1e9
    )
    return local_filepaths
