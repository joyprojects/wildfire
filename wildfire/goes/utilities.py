"""Utilities to use across modules in the goes sub-package."""
import datetime
import logging
import multiprocessing
import os
import re

import numpy as np

SATELLITE_CONVERSION = {
    # satellite shorthand: satellite bucket name
    "G16": "noaa-goes16",
    "G17": "noaa-goes17",
}
REGION_TIME_RESOLUTION_MINUTES = {"M1": 1, "M2": 1, "C": 5, "F": 15}

_logger = logging.getLogger(__name__)


def pool_function(function, function_args, num_workers=None):
    """Run `function` across multiple workers in parallel.

    User should read documentation on `multiprocessing.Pool` before using this method.
    https://docs.python.org/3.7/library/multiprocessing.html

    Parameters
    ----------
    function : function
        Function to pool across multiple threads.
    function_args : iterable
        Arguments to iteratively pass to `function` across multiple threads. All elements
        must be pickleable.
    num_workers : int
        Optional, the number of workers over which to pool `function`. Defaults to `None`
        in which case it will be set to the number of cores on the machine. If not `None`,
        it must be less than or equal to the number of cores available on the machine.

    Returns
    -------
    list of Any
        An iterator over the return values of `function` across the number of threads.
        Length is `num_workers`.
    """
    max_workers_allowed = multiprocessing.cpu_count()
    num_workers = num_workers if num_workers is not None else max_workers_allowed

    if num_workers > max_workers_allowed:
        _logger.info(
            "Setting `num_threads` from %d to %d, since machine has %d cores.",
            num_workers,
            max_workers_allowed,
            max_workers_allowed,
        )
        num_workers = max_workers_allowed
    _logger.info("Pooling function '%s' over %d workers", function.__name__, num_workers)
    with multiprocessing.Pool(processes=num_workers) as pool:
        results = pool.map(func=function, iterable=function_args)
    return results


def create_time_range(start, end, minutes):
    """Create time range from `start` to `end` .

    Parameters
    ----------
    start : datetime.datetime
    end : datetime.datetime
    minutes : int
        Number of minutes to add to the previous datetime element to get the next one.

    Returns
    -------
        list of datetime.datetime
    """
    time_range = []
    current = start
    while current <= end:
        time_range.append(current)
        current += datetime.timedelta(minutes=minutes)
    return time_range


def normalize(data):
    """Normalize data to be centered around 0.

    Parameters
    ----------
    data : np.ndarray | xr.core.dataarray.DataArray

    Returns
    -------
    np.ndarray | xr.core.dataarray.DataArray
    """
    return (data - data.mean()) / data.std()


def find_scans_closest_to_times(s3_scans, desired_times):
    """Find all scans in set with the closest scan start time to the desired time.

    If multiple bands were requested when producing `s3_scans` then that the number
    of bands requested should match the number of scans returned by this method.

    Parameters
    ----------
    s3_scans : list of boto3.resources.factory.s3.ObjectSummary
    desired_times : list of datetime.datetime

    Returns
    -------
    np.ndarray of str
        Where each element is the S3 file path.
    """
    scan_times = np.array([parse_filename(s3_scan.key)[3] for s3_scan in s3_scans])
    closest_times = scan_times[
        np.argmin(np.abs([scan_times - scan_time for scan_time in desired_times]), axis=1)
    ]
    closest_scans = [
        np.array(s3_scans)[np.where(scan_times == closest_time)]
        for closest_time in closest_times
    ]

    if len(desired_times) == 1:
        closest_scans = closest_scans[0]

    return np.vectorize(lambda s3_scan: f"s3://{s3_scan.bucket_name}/{s3_scan.key}")(
        closest_scans
    )


def build_local_path(local_directory, filepath, satellite):
    """Build local path (matched S3 file structure).

    Parameters
    ----------
    local_directory : str
    filepath : str
    satellite : str

    Returns
    -------
    str
        e.g. {local_directory}/noaa-goes17/ABI-L1b-RadM/2019/300/20/
        OR_ABI-L1b-RadM1-M6C14_G17_s20193002048275_e20193002048332_c20193002048405.nc
    """
    return os.path.join(local_directory, satellite, filepath)


def parse_filename(filename):
    """Parse necessary information from the filename.

    This method also verifies correct filename input.

    Examples
    --------
    OR_ABI-L1b-RadM1-M6C14_G17_s20193002048275_e20193002048332_c20193002048405.nc
    Region = M1
    Channel = 14
    Satellite = noaa-goes17
    Scan Start Time = 2019-10-27 20:48:27.5

    Parameters
    ----------
    filename : str

    Returns
    -------
    tuple of (str, int, str, datetime.datetime)
        region, channel, satellite, started_at
    """
    region, channel, satellite, started_at = re.search(
        r"OR_ABI-L1b-Rad(.*)-M\dC(\d{2})_(G\d{2})_s(.*)_e.*_c.*.nc", filename
    ).groups()
    started_at = datetime.datetime.strptime(started_at, "%Y%j%H%M%S%f")
    satellite = SATELLITE_CONVERSION[satellite]
    channel = int(channel)
    return region, channel, satellite, started_at
