"""Common utilities for the GOES level 1 data.."""
import datetime
import glob
import logging
import os
import re

import numpy as np

from wildfire import multiprocessing

SATELLITE_SHORT_HAND = {"noaa-goes16": "G16", "noaa-goes17": "G17"}
SATELLITE_LONG_HAND = {"G16": "noaa-goes16", "G17": "noaa-goes17"}
BASE_PATTERN_FORMAT = os.path.join(
    "{directory}",
    "ABI-L1b-Rad{region[0]}",
    "{year}",
    "{day_of_year}",
    "{hour}",
    "OR_ABI-L1b-Rad{region}-M?C{channel}_{satellite_short}_s{start_time}*.nc",
)

_logger = logging.getLogger(__name__)


def group_filepaths_into_scans(filepaths):
    """Group bands in `filepaths` that belong to the same scan.

    A scan is defined as files that have the same satellite, region, and scan start time.

    Parameters
    ----------
    filepaths : list of str

    Returns
    -------
    list of list of str
        Each sublist is a specific scan.
    """
    scan_times = [parse_filename(filepath)[3] for filepath in filepaths]
    unique_scan_times, unique_indices = np.unique(scan_times, return_inverse=True)
    groups = [[] for i in range(len(unique_scan_times))]
    for scan_time_idx, unique_idx in enumerate(unique_indices):
        groups[unique_idx].append(filepaths[scan_time_idx])
    return groups


def decide_fastest_glob_patterns(
    directory, satellite, region, start_time, end_time, channel=None, s3=False
):
    """From the provided input, compile the glob patterns for multiprocessing.

    Parameters
    ----------
    directory : str
        Local directory in which to search for files.
    satellite : str
        Must be in set (noaa-goes16, noaa-goes17).
    region : str
        Must be in set (M1, M2, C, F).
    channel : int, optional
        Must be between 1 and 16 inclusive. Default to `None` which sets channel to
        `"??"` to match all channels.
    start_time : datetime.datetime
    end_time : datetime.datetime
    s3 : bool, optional
        Whether glob patterns should be formatted for s3 filepaths or local filepaths. By
        default False, which formats glob patterns for the local filesystem.

    Returns
    -------
    list of str
    """
    channel = str(channel).zfill(2) if channel is not None else "??"
    base_pattern = (
        BASE_PATTERN_FORMAT if not s3 else BASE_PATTERN_FORMAT.replace(os.sep, "/")
    )

    satellite_short = SATELLITE_SHORT_HAND[satellite]
    if end_time is None:
        return [
            base_pattern.format(
                directory=directory,
                satellite_short=satellite_short,
                region=region,
                year=start_time.strftime("%Y"),
                day_of_year=start_time.strftime("%j"),
                hour=start_time.strftime("%H"),
                start_time=start_time.strftime("%Y%j%H%M"),
                channel=channel,
            )
        ]

    if start_time.year != end_time.year:
        return [
            base_pattern.format(
                directory=directory,
                satellite_short=satellite_short,
                region=region,
                year=str(year),
                day_of_year="*",
                hour="*",
                start_time="*",
                channel=channel,
            )
            for year in range(start_time.year, end_time.year + 1)
        ]

    if start_time.date() != end_time.date():
        return [
            base_pattern.format(
                directory=directory,
                satellite_short=satellite_short,
                region=region,
                year=start_time.strftime("%Y"),
                day_of_year=str(day_of_year).zfill(3),
                hour="*",
                start_time="*",
                channel=channel,
            )
            for day_of_year in range(
                int(start_time.strftime("%j")), int(end_time.strftime("%j")) + 1
            )
        ]

    if start_time.hour != end_time.hour:
        return [
            base_pattern.format(
                directory=directory,
                satellite_short=satellite_short,
                region=region,
                year=start_time.strftime("%Y"),
                day_of_year=start_time.strftime("%j"),
                hour=str(hour).zfill(2),
                start_time="*",
                channel=channel,
            )
            for hour in range(start_time.hour, end_time.hour + 1)
        ]

    return [
        base_pattern.format(
            directory=directory,
            satellite_short=satellite_short,
            region=region,
            year=start_time.strftime("%Y"),
            day_of_year=start_time.strftime("%j"),
            hour=start_time.strftime("%H"),
            start_time="*",
            channel=channel,
        )
    ]


def filter_filepaths(filepaths, start_time, end_time):
    """Remove filepaths that are outside of `start_time` and `end_time`.

    Parameters
    ----------
    filepaths : list of str
    start_time : datetime.datetime
    end_time : datetime.datetime

    Returns
    -------
    list of str
    """
    return [
        filepath
        for filepath in filepaths
        if start_time <= parse_filename(filename=filepath)[3] <= end_time
    ]


def list_local_files(
    local_directory, satellite, region, start_time, end_time=None, channel=None
):
    """List local files that match parameters.

    Only parallelizes across locally available hardware.

    Parameters
    ----------
    local_directory : str
        Local directory for which to list files.
    satellite : str
        Must be in set (noaa-goes16, noaa-goes17).
    region : str
        Must be in set (M1, M2, C, F).
    channel : int, optional
        Must be between 1 and 16 inclusive. By default `None` which will list all
        channels.
    start_time : datetime.datetime
    end_time : datetime.datetime, optional
        By default `None`, which will list all files whose scan start time matches
        `start_time`.

    Returns
    -------
    list of str
    """
    glob_patterns = decide_fastest_glob_patterns(
        directory=local_directory,
        satellite=satellite,
        region=region,
        channel=channel,
        start_time=start_time,
        end_time=end_time,
    )
    # only parallel across local hardware
    filepaths = multiprocessing.map_function(glob.glob, glob_patterns)
    if len(filepaths) < 0:
        raise ValueError(f"No files found using patterns {glob_patterns}")

    filepaths = multiprocessing.flatten_array(filepaths)
    if end_time is not None:
        return filter_filepaths(
            filepaths=filepaths, start_time=start_time, end_time=end_time,
        )
    return filepaths


def parse_filename(filename):
    """Parse region, channel, satellite and started_at from filename.

    Parameters
    ----------
    filename : str
        Either a filepath or filename for a goes scan. Must be of the form:
            OR_ABI-L1b-RadM1-M6C01_G17_s20193351027275_e20193351027332_c20193351027383.nc

    Returns
    -------
    tuple of (str, int, str, datetime.datetime)
        region, channel, satellite, started_at
    """
    region, channel, satellite, started_at = re.search(
        r"OR_ABI-L1b-Rad(.*)-M\dC(\d{2})_(G\d{2})_s(.*)_e.*_c.*.nc", filename
    ).groups()
    started_at = datetime.datetime.strptime(started_at, "%Y%j%H%M%S%f")
    channel = int(channel)
    return region, channel, satellite, started_at
