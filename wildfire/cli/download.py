"""Download wildfire data."""
import logging
import os
import subprocess

import click
from mpi4py import MPI
import numpy as np

from wildfire.data.goes_level_1 import downloader

DATETIME_FORMATS = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@click.group()
def download():
    """Download wildfire data."""
    pass


@download.command()
@click.argument("start", type=click.DateTime(formats=DATETIME_FORMATS))
@click.argument("end", type=click.DateTime(formats=DATETIME_FORMATS))
@click.option(
    "--satellite",
    default="noaa-goes17",
    type=click.Choice(["noaa-goes16", "noaa-goes17"]),
    help="GOES East|GOES East.",
)
@click.option(
    "--region",
    default="M1",
    type=click.Choice(["M1", "M2", "C", "F"]),
    help="US West Coast|US East Coast|US Full|Hemisphere.",
)
@click.option(
    "--persist_directory",
    default="./downloaded_data",
    type=click.Path(exists=True, file_okay=False),
    help="Directory in which to look for or download GOES data.",
)
def goes_level_1(start, end, satellite, region, persist_directory):
    """Download GOES Level 1b data from Amazon S3.

    Usage: `download goes-level-1 2019-01-01 2019-02-01`
    """
    _logger.info(
        """Downloading available GOES satellite data. Parameters:
    Satellite: %s
    Regions: %s
    Channels: %s
    Start Time: %s
    End Time: %s""",
        satellite,
        region,
        list(range(1, 17)),
        start,
        end,
    )
    downloader.download_files(
        local_directory=persist_directory,
        satellite=satellite,
        region=region,
        start_time=start,
        end_time=end,
    )
    _logger.info("Success.")


@download.command()
@click.argument("year")
@click.argument("day_of_year_min")
@click.argument("day_of_year_max")
@click.option(
    "--satellite",
    default="noaa-goes16",
    type=click.Choice(["noaa-goes16", "noaa-goes17"]),
    help="GOES East|GOES East.",
)
@click.option(
    "--product",
    default="ABI-L2-FDCF",
    type=click.Choice(["ABI-L2-FDCF", "ABI-L2-FDCC"]),
    help="Hemisphere Fire Scans|US Full Fire Scans.",
)
@click.option(
    "--persist_directory",
    default="./downloaded_data",
    type=click.Path(exists=True, file_okay=False),
    help="Directory in which to look for or download GOES data.",
)
def goes_level_2(
    year, day_of_year_min, day_of_year_max, satellite, product, persist_directory
):
    """Download GOES level 2 fire data.

    Usage: `mpirun -np 32 download goes-level-2 2020 001 010`
    """
    comm = MPI.COMM_WORLD
    process_rank = comm.Get_rank()
    num_processes = comm.Get_size()

    days = None
    if process_rank == 0:
        _logger.info(
            """Downloading available GOES satellite data. Parameters:
        Satellite: %s
        Product: %s
        Year: %s
        Day of Year Start: %s
        Day of Year End: %s
        Persist Directory: %s
        Num Processes: %s""",
            satellite,
            product,
            year,
            day_of_year_min,
            day_of_year_max,
            persist_directory,
            num_processes,
        )
        days = list(range(day_of_year_min, day_of_year_max + 1))
        days = np.array_split(days, indices_or_sections=num_processes)

    days = comm.scatter(days)
    for day_of_year in days:
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
    _logger.info("Rank %s completed.", process_rank)


@download.command()
def modis():
    """Not yet implemented."""
    pass
