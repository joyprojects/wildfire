"""Download GOES level 2 fire data."""
import logging
import os
import subprocess

from wildfire import multiprocessing


_logger = logging.getLogger(__name__)


def download_day(year, day_of_year, satellite, product, persist_directory):
    """Download a day of GOES L2 Fire data.

    Parameters
    ----------
    year : str
    day_of_year : str
        1 through 365.
    satellite : str
        Must be either "noaa-goes16" or "noaa-goes17"
    product : str
        Must be either "ABI-L2-FDCC" or "ABI-L2-FDCF".
    persist_directory : str

    Returns
    -------
    str
        Local filepath to downloaded file.
    """
    _logger.info("Downloading fire data for %s-%s...", year, day_of_year)
    subprocess.check_call(
        [
            "aws",
            "s3",
            "cp",
            f"s3://{satellite}/{product}/{year}/{day_of_year}/",
            os.path.join(persist_directory, satellite, product, year, day_of_year),
            "--recursive",
        ]
    )


def download_batch(year, days, satellite, product, persist_directory):
    """Download a set of GOES level 2 fire data.

    Parameters
    ----------
    year : str
    days : list of int
        List of integers, where each integer must be between 1 and 365.
    satellite : str
        Must be either "noaa-goes16" or "noaa-goes17"
    product : str
        Must be either "ABI-L2-FDCC" or "ABI-L2-FDCF".
    persist_directory : str

    Returns
    -------
    str
        The list of filepaths where data was downloaded.
    """
    _logger.info("Downloading batch of fire data...")
    year = str(year)
    download_args = [
        [year] * len(days),
        [f"{day_of_year:03d}" for day_of_year in days],
        [satellite] * len(days),
        [product] * len(days),
        [persist_directory] * len(days),
    ]
    multiprocessing.map_function(function=download_day, function_args=download_args)
    _logger.info("Downloaded files to %s", persist_directory)
