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
    satellite : str
    product : str
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
    _logger.info("Downloading batch of fire data...")
    year = str(year)
    download_args = [
        [year] * len(days),
        [f"{day_of_year:03d}" for day_of_year in days],
        [satellite] * len(days),
        [product] * len(days),
        [persist_directory] * len(days),
    ]
    filepaths = multiprocessing.map_function(
        function=download_day, function_args=download_args
    )
    _logger.info("Downloaded %d files to %s", len(filepaths), persist_directory)
    return filepaths
