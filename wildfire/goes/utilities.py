import datetime
import glob
import logging
import multiprocessing
import re

import numpy as np
import s3fs
import tqdm

from wildfire.goes import downloader

LOCAL_FILEPATH_FORMAT = "{local_directory}/{s3_key}"
SATELLITE_SHORT_HAND = {"noaa-goes16": "G16", "noaa-goes17": "G17"}


_logger = logging.getLogger(__name__)


def decide_fastest_glob_patterns(directory, satellite, region, start_time, end_time):
    base_pattern = "{directory}/ABI-L1b-Rad{region[0]}/{year}/{day_of_year}/{hour}/OR_ABI-L1b-Rad{region}-M?C??_{satellite_short}_s{start_time}*.nc"

    satellite_short = SATELLITE_SHORT_HAND[satellite]
    if end_time is None:
        return [
            base_pattern.format(
                satellite=directory,
                satellite_short=satellite_short,
                region=region,
                year=start_time.strftime("%Y"),
                day_of_year=start_time.strftime("%j"),
                hour=start_time.strftime("%H"),
                start_time=start_time.strftime("%Y%j%H%M"),
            )
        ]

    if start_time.year != end_time.year:
        return [
            base_pattern.format(
                satellite=satellite,
                satellite_short=satellite_short,
                region=region,
                year=str(year),
                day_of_year="*",
                hour="*",
                start_time="*",
            )
            for year in range(start_time.year, end_time.year + 1)
        ]

    if start_time.date() != end_time.date():
        return [
            base_pattern.format(
                satellite=satellite,
                satellite_short=satellite_short,
                region=region,
                year=start_time.strftime("%Y"),
                day_of_year=str(day_of_year).zfill(3),
                hour="*",
                start_time="*",
            )
            for day_of_year in range(
                int(start_time.strftime("%j")), int(end_time.strftime("%j")) + 1
            )
        ]

    if start_time.hour != end_time.hour:
        return [
            base_pattern.format(
                satellite=satellite,
                satellite_short=satellite_short,
                region=region,
                year=start_time.strftime("%Y"),
                day_of_year=start_time.strftime("%j"),
                hour=str(hour).zfill(2),
                start_time="*",
            )
            for hour in range(start_time.hour, end_time.hour + 1)
        ]

    return [
        base_pattern.format(
            satellite=satellite,
            satellite_short=satellite_short,
            region=region,
            year=start_time.strftime("%Y"),
            day_of_year=start_time.strftime("%j"),
            hour=start_time.strftime("%H"),
            start_time="*",
        )
    ]


def filter_filepaths(filepaths, start_time, end_time):
    return [
        filepath
        for filepath in filepaths
        if start_time <= parse_filename(filename=filepath)[3] <= end_time
    ]


def list_local_files(local_directory, satellite, region, start_time, end_time=None):
    glob_patterns = decide_fastest_glob_patterns(
        directory=local_directory,
        satellite=satellite,
        region=region,
        start_time=start_time,
        end_time=end_time,
    )
    glob_patterns = [
        "/".join([local_directory] + pattern.split("/")[1:]) for pattern in glob_patterns
    ]
    _logger.info("Listing local files using glob patterns: %s", glob_patterns)
    return map_function(glob.glob, glob_patterns, flatten=True)


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


def s3_filepath_to_local(s3_filepath, local_directory):
    _, key = s3fs.core.split_path(s3_filepath)
    return LOCAL_FILEPATH_FORMAT.format(local_directory=local_directory, s3_key=key)


def parse_filename(filename):
    region, channel, satellite, started_at = re.search(
        r"OR_ABI-L1b-Rad(.*)-M\dC(\d{2})_(G\d{2})_s(.*)_e.*_c.*.nc", filename
    ).groups()
    started_at = datetime.datetime.strptime(started_at, "%Y%j%H%M%S%f")
    channel = int(channel)
    return region, channel, satellite, started_at


def map_function(function, function_args, flatten=False):
    # TODO add error handling
    _logger.info(
        "Using %s workers to run %s...", multiprocessing.cpu_count(), function.__name__
    )
    with multiprocessing.Pool() as pool:
        worker_results = pool.map(function, function_args)
    if flatten:
        return _flatten(worker_results)
    return worker_results


def imap_function(function, function_args, flatten=False):
    # TODO add error handling
    _logger.info(
        "Using %s workers to run %s...", multiprocessing.cpu_count(), function.__name__
    )
    with multiprocessing.Pool() as pool:
        worker_map = pool.imap(function, function_args)
        worker_results = list(tqdm.tqdm(worker_map, total=len(function_args)))

    if flatten:
        return _flatten(worker_results)
    return worker_results


def starmap_function(function, function_args, flatten=False):
    # TODO add error handling
    _logger.info(
        "Using %s workers to run %s...", multiprocessing.cpu_count(), function.__name__
    )
    with multiprocessing.Pool() as pool:
        worker_results = pool.starmap(function, function_args)
    if flatten:
        return _flatten(worker_results)
    return worker_results


def _flatten(list_2d):
    return [item for list_1d in list_2d for item in list_1d]


def group_filepaths_into_scans(filepaths):
    scan_times = [parse_filename(filepath)[3] for filepath in filepaths]
    unique_scan_times, unique_indices = np.unique(scan_times, return_inverse=True)
    groups = [[] for i in range(len(unique_scan_times))]
    for scan_time_idx, unique_idx in enumerate(unique_indices):
        groups[unique_idx].append(filepaths[scan_time_idx])
    return groups
