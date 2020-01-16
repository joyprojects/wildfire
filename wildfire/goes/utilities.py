import datetime
import logging
import multiprocessing
import re

import numpy as np
import s3fs
import tqdm

LOCAL_FILEPATH_FORMAT = "{local_directory}/{s3_key}"


_logger = logging.getLogger(__name__)


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
