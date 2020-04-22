"""Create model predictions.

This module uses `ray` so that it can also be distributed across compute nodes.
"""
import datetime
import json
import logging
import os

import click

from wildfire import multiprocessing, wildfire
from wildfire.data import goes_level_1

DATETIME_FORMATS = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]
WILDFIRE_FILENAME = "wildfires_{satellite}_{region}_s{start}_e{end}_c{created}.json"

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@click.group()
def predict():
    """Use the wildfire models to predict."""
    pass


@predict.command()
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
    "--goes_directory",
    default="./downloaded_data",
    type=click.Path(exists=True, file_okay=False),
    help="Directory in which to look for or download GOES data.",
)
@click.option(
    "--wildfire_directory",
    default="./labeled_data",
    type=click.Path(exists=True, file_okay=False),
    help="Directory in which to persist wildfires.",
)
@click.option("--download", is_flag=True, help="Download from S3?")
def goes_threshold(
    start, end, satellite, region, goes_directory, wildfire_directory, download
):
    """Label wildfires in GOES Level 1b data.

    Usage: `predict goes-threshold 2019-01-01 2019-01-02`
    """
    if download:
        filepaths = goes_level_1.downloader.download_files(
            local_directory=goes_directory,
            satellite=satellite,
            region=region,
            start_time=start,
            end_time=end,
        )
    else:
        filepaths = goes_level_1.utilities.list_local_files(
            local_directory=goes_directory,
            satellite=satellite,
            region=region,
            start_time=start,
            end_time=end,
        )
        if not filepaths:
            raise ValueError("No local files found...")

    scan_filepaths = goes_level_1.utilities.group_filepaths_into_scans(
        filepaths=filepaths
    )
    _logger.info(
        """Labeling wildfires from GOES data with the threshold model.
    Satellite: %s
    Region: %s
    Start Time: %s
    End Time: %s
    GOES Directory: %s
    Persist Directory: %s
    Num Processes: %s,
    Num Scans: %s""",
        satellite,
        region,
        start,
        end,
        goes_directory,
        wildfire_directory,
        os.cpu_count(),
        len(scan_filepaths),
    )

    wildfires = multiprocessing.map_function(
        function=wildfire.parse_scan_for_wildfire, function_args=[scan_filepaths]
    )
    wildfires = list(filter(None, wildfires))
    _logger.info("Found %d wildfires.", len(wildfires))

    wildfires = multiprocessing.flatten_array(wildfires)
    if len(wildfires) > 0:
        wildfires_filepath = os.path.join(
            wildfire_directory,
            WILDFIRE_FILENAME.format(
                satellite=satellite,
                region=region,
                start=start.strftime(DATETIME_FORMATS[0]),
                end=end.strftime(DATETIME_FORMATS[0]),
                created=datetime.datetime.utcnow().strftime(DATETIME_FORMATS[0]),
            ),
        )
        _logger.info("Persisting wildfires to %s", wildfires_filepath)
        with open(wildfires_filepath, "w+") as buffer:
            json.dump(dict(enumerate(wildfires)), buffer)
    else:
        _logger.info("No wildfires found...")

    _logger.info("Success.")


@predict.command
def goes_deep():
    """Not yet implemented."""
    pass
